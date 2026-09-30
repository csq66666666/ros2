# ROS 2 工作区梳理：status_interfaces / status_publisher / status_display

> 工作区根目录：`/home/csq/ros2/2`　ROS 版本：Humble　构建工具：colcon

---

## 一、为什么要拆成三个包

一句话：**把「数据长什么样」「谁生产数据」「谁消费数据」三件事分开**。

| 包 | 构建类型 | 角色 | 一句话 |
|---|---|---|---|
| `status_interfaces` | `ament_cmake` | **契约层** | 只定义消息格式，不干活 |
| `status_publisher` | `ament_python` | **生产者** | 采集 CPU/内存/网络，发布出去 |
| `status_display` | `ament_cmake` | **消费者** | 订阅并画到 Qt 窗口上 |

拆开的最大好处：**发布者用 Python、显示用 C++，两者语言不同却能互通**，因为它们共享同一份 `.msg` 定义。如果消息定义各自手写，两边字段顺序/类型稍有出入，通信就会静默失败。

---

## 二、全景依赖图

```
                    ┌───────────────────────────────────┐
                    │        status_interfaces          │
                    │        (ament_cmake)              │
                    │                                   │
                    │   msg/SystemStatus.msg            │
                    │   ┌─────────────────────────────┐ │
                    │   │ builtin_interfaces/Time stamp│ │
                    │   │ string   host_name           │ │
                    │   │ float32  cpu_percent         │ │
                    │   │ float32  memory_percent      │ │
                    │   │ float32  memory_total        │ │
                    │   │ float32  memory_available    │ │
                    │   │ float64  net_sent            │ │
                    │   │ float64  net_recv            │ │
                    │   └─────────────────────────────┘ │
                    └────────────┬──────────────────────┘
                                 │
                    「被两个包同时依赖」
                                 │
                 ┌───────────────┴───────────────┐
                 │                               │
                 ▼                               ▼
   ┌──────────────────────────┐   ┌──────────────────────────┐
   │    status_publisher      │   │     status_display       │
   │    (ament_python)        │   │     (ament_cmake)        │
   │                          │   │                          │
   │  sys_status_pub.py       │   │  sys_status_display.cpp  │
   │  ┌────────────────────┐  │   │  ┌────────────────────┐  │
   │  │ rclpy              │  │   │  │ rclcpp             │  │
   │  │ psutil  ◄── 系统    │  │   │  │ Qt5::Widgets ◄─ GUI │  │
   │  │ platform           │  │   │  └────────────────────┘  │
   │  └────────────────────┘  │   │                          │
   └───────────┬──────────────┘   └───────────▲──────────────┘
               │                              │
               │      话题 /system_status      │
               │   （唯一的运行时耦合点！）      │
               └──────────────────────────────┘
```

**关键理解**：编译期三个包通过 `package.xml` 的 `<depend>` 形成依赖；运行期两个节点之间**只通过话题名 + 消息类型耦合**，彼此不知道对方存在，也不关心对方是 Python 还是 C++。

---

## 三、构建流水线（colcon 自动拓扑排序）

`colcon build` 会读所有 `package.xml`，自动排出顺序，**你不需要手动指定先后**：

```
colcon build
      │
      ├─ 第 1 步：status_interfaces        （谁都不依赖，先建）
      │           生成代码 + 编译 typesupport 库
      │
      ├─ 第 2 步：同时并行 ─┬─ status_publisher   （依赖 interfaces）
      │                    └─ status_display     （依赖 interfaces）
      ▼
   install/ 目录（overlay）
```

如果 `status_interfaces` 编译失败，后两个包**根本不会被构建**——这是新手常见困惑来源。

---

## 四、status_interfaces 详解（契约层）

### 4.1 三个文件的分工

```
src/status_interfaces/
├── msg/SystemStatus.msg      ← 唯一的真值来源（Single Source of Truth）
├── CMakeLists.txt            ← 告诉 rosidl「把 .msg 变成代码」
└── package.xml               ← 声明「我是接口包」
```

### 4.2 CMakeLists.txt 关键三行

```cmake
find_package(rosidl_default_generators REQUIRED)   # ① 拿到「消息生成器」这个工具

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/SystemStatus.msg"
  DEPENDENCIES builtin_interfaces                  # ② 因为 msg 里用了 builtin_interfaces/Time
)

ament_package()
```

`find_package(builtin_interfaces REQUIRED)` 也在上面——**`.msg` 里每用到一个外部类型，这里就要加一次 `DEPENDENCIES`**，两处必须成对出现。

### 4.3 生成产物（一次 `.msg` → 四套代码）

```
              msg/SystemStatus.msg
                       │
                       │  rosidl_generate_interfaces()
                       ▼
   ┌───────────────────┼───────────────────┬────────────────────┐
   ▼                   ▼                   ▼                    ▼
 C++ 头文件         Python 模块        C 类型支持          introspection
 install/.../       install/.../       libstatus_          （供 ros2 topic
 include/status_    local/lib/         interfaces__        echo 等工具
 interfaces/        python3.10/        rosidl_*.so         动态解析用）
 status_interfaces/ dist-packages/
 msg/system_        status_interfaces/
 status.hpp         msg/_system_status.py
   │                   │
   │                   └──► from status_interfaces.msg import SystemStatus   (Python 侧)
   └──► #include <status_interfaces/msg/system_status.hpp>                    (C++ 侧)
```

> 注意大小写转换：`.msg` 里的 `SystemStatus` → C++ 头文件是 **小写下划线** `system_status.hpp`，Python 类名保持 `SystemStatus`。这个不对称是很多人 `#include` 写错的根源。

### 4.4 package.xml 里的「接口包身份证」

```xml
<buildtool_depend>rosidl_default_generators</buildtool_depend>  <!-- 生成期 -->
<depend>builtin_interfaces</depend>                             <!-- 依赖 -->
<exec_depend>rosidl_default_runtime</exec_depend>               <!-- 运行期 -->
<member_of_group>rosidl_interface_packages</member_of_group>    <!-- ★ 关键 -->
```

`<member_of_group>rosidl_interface_packages</member_of_group>` **千万不能删**——它让 rosidl 的 CMake 宏在其它包里能被正确找到。漏了它，下游包 `find_package` 会失败。

---

## 五、status_publisher 详解（Python 包）

Python 包没有 CMakeLists，取而代之的是 **`setup.py` + `setup.cfg` + `resource/` 三件套**，这是最容易懵的地方。

### 5.1 五个文件的关系

```
src/status_publisher/
├── package.xml                        ← ROS 元信息 + 依赖 + 声明构建类型
├── setup.py                           ← 装什么、命令叫什么
├── setup.cfg                          ← 命令装到哪 ★ 决定 ros2 run 能否找到
├── resource/status_publisher          ← 0 字节空文件，纯「标记」
└── status_publisher/                  ← 真正的 Python 包（有 __init__.py）
    ├── __init__.py
    └── sys_status_pub.py              ← 含 main()
```

### 5.2 setup.py 三段落

```python
package_name = 'status_publisher'

data_files=[                                              # ── 段落 A：装「非代码」文件
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),                    # ① 标记文件 → 让 ament 索引发现本包
    ('share/' + package_name, ['package.xml']),           # ② 元信息 → 让 ros2 pkg 能读
],

entry_points={                                            # ── 段落 B：造「命令」
    'console_scripts': [
        'sys_status_pub = status_publisher.sys_status_pub:main',
        #    ↑命令名            ↑包名.模块名      ↑函数名
    ],
},
packages=find_packages(exclude=['test'])                  # ── 段落 C：装「代码」
```

**段落 A 的两行各司其职，缺一不可**：

- 少了 ①：`ros2 run`、`ros2 pkg list` **看不到这个包**
- 少了 ②：`ros2 pkg xml status_publisher`、`colcon` 解析依赖会出问题

`resource/status_publisher` 内容为空是**正确的**，它只是个「到此一游」标记，ros2 靠文件名而非内容识别。

### 5.3 setup.cfg —— 最隐蔽但最关键的一环

```ini
[develop]
script_dir=$base/lib/status_publisher
[install]
install_scripts=$base/lib/status_publisher
```

**为什么需要它？** 默认 pip/setuptools 会把 `sys_status_pub` 这个入口脚本装到 `<prefix>/bin/`。但 `ros2 run <pkg> <exe>` 只去 **`<prefix>/lib/<pkg>/`** 找可执行文件。这个配置就是把脚本「挪」到 ros2 期望的位置：

```
   没有 setup.cfg                      有 setup.cfg
   ────────────────                    ────────────────
   install/status_publisher/bin/       install/status_publisher/lib/status_publisher/
        sys_status_pub                       sys_status_pub
             │                                    │
             ✗ ros2 run 找不到                     ✓ ros2 run status_publisher sys_status_pub
```

### 5.4 名字必须一致的五处（改包名时的雷区）

```
 package.xml             <name>status_publisher</name>  ┐
 setup.py                package_name = 'status_publisher'│
 目录名                  status_publisher/               ├─ 必须完全相同
 resource/<文件名>        resource/status_publisher       │
 setup.py entry_points   'status_publisher.sys_status_pub:main'
```

任何一处不一致，症状往往是「`ros2 run` 说找不到可执行文件」或「No module named ...」，且报错信息不直接指向真凶。

---

## 六、status_display 详解（C++ / Qt 包）

### 6.1 CMakeLists.txt 逐行

```cmake
find_package(rclcpp REQUIRED)              # ROS 2 C++ 客户端库
find_package(status_interfaces REQUIRED)   # ★ 拿到上一步生成的头文件
find_package(Qt5 REQUIRED COMPONENTS Widgets)

# hello_qt：纯 Qt 示例，不涉及 ROS
add_executable(hello_qt src/hello_qt.cpp)
target_link_libraries(hello_qt Qt5::Widgets)

# sys_status_display：Qt + ROS 混合
add_executable(sys_status_display src/sys_status_display.cpp)

ament_target_dependencies(sys_status_display rclcpp status_interfaces)  # ★ ROS 依赖
target_link_libraries(sys_status_display Qt5::Widgets)                 # ★ Qt 依赖
target_include_directories(sys_status_display PRIVATE ${Qt5Widgets_INCLUDE_DIRS})
```

### 6.2 为什么 ROS 和 Qt 要用两种不同写法

```
   ament_target_dependencies(目标 rclcpp status_interfaces)
        └─► 认识「ROS 包」，自动补 include 路径 + 链接库 + 编译定义
            但它不认识 Qt5！

   target_link_libraries(目标 Qt5::Widgets)
        └─► CMake 原生写法，处理「非 ROS 的第三方库」

   ⟹ 所以一个目标必须同时写这两行，缺任一都会编译/链接失败
```

注释里写的「顺序很关键」意思是：先让 `ament_target_dependencies` 建立 ROS 环境，再追加 Qt，这样两套 include 路径不会互相覆盖。

### 6.3 安装规则 —— 与 Python 侧殊途同归

```cmake
install(TARGETS hello_qt sys_status_display DESTINATION lib/${PROJECT_NAME})
                                                             ↑
                                                    即 lib/status_display/
```

对照第五节：Python 靠 `setup.cfg` 把脚本放到 `lib/status_publisher/`，C++ 靠 `install(... DESTINATION lib/...)` 放到 `lib/status_display/`。**两种语言最终都落在 `<prefix>/lib/<包名>/`，所以 `ros2 run` 的用法完全统一**：

```bash
ros2 run status_publisher sys_status_pub      # Python
ros2 run status_display   sys_status_display  # C++
```

---

## 七、运行时数据流（消息的一生）

```
  ① 定时器 1Hz 触发
        │
        ▼
  sys_status_pub.py: timer_callback()
        │
        ├─ psutil.cpu_percent()          ┐
        ├─ psutil.virtual_memory()       │ ② 采集系统数据
        ├─ psutil.net_io_counters()      ┘
        │
        ▼
  ③ 填入 SystemStatus() 对象（Python 类实例）
        │
        ▼
  ④ self.status_publisher_.publish(msg)
        │
        ▼
  ╔═══════════════════════════════════════════════════╗
  ║  ⑤ DDS 中间件（Humble 默认 Fast-DDS）               ║
  ║     按【话题名 + 类型 + QoS】做匹配                  ║
  ║     /system_status + SystemStatus + RELIABLE/VOLATILE
  ╚═══════════════════════════════════════════════════╝
        │
        │  ← 这里就是之前「收不到」的断点：
        │     之前订阅端写的是 /sys_status，名字对不上，DDS 不投递
        ▼
  ⑥ sys_status_display.cpp 回调被触发（在 spin 线程里！）
        │
        ▼
  ⑦ get_qstr_from_msg(msg) → 拼成 QString
        │
        ▼
  ⑧ label_->setText(...)  ⚠️ 在非 GUI 线程操作控件（未定义行为）
        │
        ▼
  Qt 主线程重绘窗口
```

### 7.1 匹配三要素（任一对不上就静默收不到）

```
  ┌────────────────┬──────────────────────┬──────────────────────┐
  │ 要素            │ 发布端                │ 订阅端                │
  ├────────────────┼──────────────────────┼──────────────────────┤
  │ ① 话题名        │ 'system_status'      │ "system_status"  ✅已修│
  │ ② 消息类型      │ SystemStatus         │ SystemStatus     ✅   │
  │ ③ QoS          │ 10 (默认 RELIABLE)   │ 10 (默认 RELIABLE) ✅ │
  └────────────────┴──────────────────────┴──────────────────────┘
```

节点名（`system_status_pub` / `sys_status_display`）**不参与匹配**，随便起。

---

## 八、遗漏与问题清单

### 8.1 已修复

| 问题 | 位置 | 状态 |
|---|---|---|
| 话题名不一致 `sys_status` vs `system_status` | `sys_status_display.cpp:18` | ✅ 已改为 `system_status` 并重新编译 |

### 8.2 待补的依赖声明（换机器会踩）

| 缺失项 | 文件 | 应补内容 | 后果 |
|---|---|---|---|
| **`psutil` 未声明** | `src/status_publisher/package.xml` | `<depend>python3-psutil</depend>` | `rosdep install` 不会装它，换机后 `import psutil` 直接 ImportError |
| **Qt5 未声明** | `src/status_display/package.xml` | `<depend>qtbase5-dev</depend>` | 换机后 `find_package(Qt5 REQUIRED)` 失败，整个包编译不过 |

两处当前都靠**本机恰好装了**（已确认：psutil 5.9.0、Qt 5.15.3）在硬扛。补上声明才算可移植：

```xml
<!-- src/status_publisher/package.xml，与 <depend>rclpy</depend> 并列 -->
<depend>python3-psutil</depend>

<!-- src/status_display/package.xml，与 <depend>rclcpp</depend> 并列 -->
<depend>qtbase5-dev</depend>
```

（注意：`qtbase5-dev` 是 rosdep key，`find_package` 的名字是 `Qt5`，二者不同名是正常的。）

### 8.3 代码隐患（未修改）

**① Qt 跨线程刷新** — `sys_status_display.cpp:18-21`

```cpp
subscriber_ = this->create_subscription<SystemStatus>("system_status", 10, [&]
    (const SystemStatus::SharedPtr msg) -> void {
    label_->setText(get_qstr_from_msg(msg));   // ⚠️ spin 线程里直接改 Qt 控件
});
```

Qt 规定 GUI 操作只能在主线程（`app.exec()` 所在线程）。跨线程直改控件是未定义行为，典型症状是**「明明收到消息，窗口却不刷新」**或者随机崩溃。建议改法：

```cpp
subscriber_ = this->create_subscription<SystemStatus>("system_status", 10,
    [this](const SystemStatus::SharedPtr msg) -> void {
        const QString text = get_qstr_from_msg(msg);        // spin 线程里算好
        QMetaObject::invokeMethod(label_, [this, text]() {
            label_->setText(text);                          // 回到主线程刷新
        }, Qt::QueuedConnection);
    });
```

**② `[&]` 引用捕获 + `detach()`** — 同一处

原来的 `[&]` 捕获了 `node` 等局部量，而线程被 `detach()`。目前 `node` 活在 `main` 里所以侥幸没崩，但改成 `[this]` 语义更清晰、更安全。

**③ 初始占位文本** — `sys_status_display.cpp:22`

`std::make_shared<SystemStatus>()` 是默认构造（全 0），会先把窗口刷成一片 0，收到第一帧后覆盖。无害，但知道一下。

### 8.4 环境注意事项

- **每次新开终端都要 `source install/setup.bash`**，否则 `ros2 run` 找不到这三个包，也解析不了 `status_interfaces` 类型。
- `install/` 是 **overlay**，与 `/opt/ros/humble`（underlay）叠加。当前 shell 的 `AMENT_PREFIX_PATH` 只有 `/opt/ros/humble`，说明 overlay 未 source。
- **改了 `.cpp` 必须重新 `colcon build`**；`.py` 文件如果是 `--symlink-install` 装的则改完直接生效，否则也要重编。本次的教训正是「改了源码但没重编」。

---

## 九、命令速查

```bash
# ── 构建 ──────────────────────────────────────
cd /home/csq/ros2/2
source /opt/ros/humble/setup.bash
colcon build                                      # 全部（自动拓扑排序）
colcon build --packages-select status_display      # 只编一个
colcon build --symlink-install                     # Python 改动免重编（推荐）

# ── 加载 ──────────────────────────────────────
source install/setup.bash                          # ★ 每个新终端都要

# ── 运行 ──────────────────────────────────────
ros2 run status_publisher sys_status_pub          # 终端 A
ros2 run status_display   sys_status_display      # 终端 B

# ── 诊断（排查「收不到」的标准流程）───────────────
ros2 pkg list | grep status                       # 三个包是否都可见
ros2 interface show status_interfaces/msg/SystemStatus   # 消息定义
ros2 topic list                                   # 话题是否存在
ros2 topic info /system_status --verbose          # ★ 看 publisher/subscription 数量是否都 ≥1
ros2 topic echo /system_status                    # 确认真的有数据在流
ros2 node info /sys_status_display                # 看某节点的订阅列表

# ── 依赖体检 ──────────────────────────────────
ros2 pkg xml status_publisher                     # 验证 package.xml 被正确安装
rosdep check --from-paths src --ignore-src        # 检查缺失的系统依赖（补完 8.2 后应无输出）
```

**排查口诀**：`topic list` 有没有 → `topic info -v` 两端数量对不对 → 名字/类型/QoS 三要素逐一比对。
