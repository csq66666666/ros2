// ============================================================
// 第一部分：引入工具
// 这些 #include 就像“打开工具箱”，把需要用的功能提前拿进来
// ============================================================

#include <QtWidgets>        // 引入 Qt 界面工具（用来画窗口、显示文字）
#include <rclcpp/rclcpp.hpp> // 引入 ROS 2 的 C++ 工具（用来收发数据）
#include <status_interfaces/msg/system_status.hpp> // 引入自定义消息类型（数据盒子的模板）

// ============================================================
// 第二部分：给数据类型起个短名字
// 原来的名字 status_interfaces::msg::SystemStatus 太长了
// 用 using 起个短名字 SystemStatus，以后就用这个短名字
// ============================================================
using SystemStatus = status_interfaces::msg::SystemStatus;

// ============================================================
// 第三部分：定义“服务员”这个类
// class 是 C++ 里定义“一类东西”的关键词
// 这个类名叫 SysStatusDisplay，继承自 rclcpp::Node
// 意思是：它是一个 ROS 2 节点，能收发 ROS 2 的数据
// ============================================================
class SysStatusDisplay : public rclcpp::Node
{
private:
    // ========================================================
    // private 表示“私人物品”，只有这个类自己能用
    // 下面这两样是服务员的私人物品：
    // ========================================================

    // 对讲机：用来接收 ROS 2 发来的数据
    // Subscription 表示“订阅者”，SystemStatus 表示接收的数据类型
    rclcpp::Subscription<SystemStatus>::SharedPtr subscriber_;

    // 告示牌：用来在屏幕上显示文字
    // QLabel 是 Qt 里的一个控件，可以显示一段文字
    QLabel *label_;

public:
    // ========================================================
    // public 表示“公开的”，别人也能调用
    // 下面是“服务员刚上班时”要做的事（构造函数）
    // SysStatusDisplay() 就是“服务员上岗”的意思
    // : Node("sys_status_display") 表示给服务员起个名字
    // ========================================================
    SysStatusDisplay() : Node("sys_status_display")
    {
        // 造一块空白的告示牌
        label_ = new QLabel();

        // 打开对讲机，调到 "system_status" 频道，开始监听
        // "system_status" 是频道名，10 是缓冲区大小（可以不管）
        // 后面的 [&](...) 是“收到消息后要做什么”
        subscriber_ = this->create_subscription<SystemStatus>(
            "system_status", 10,
            [&](const SystemStatus::SharedPtr msg) -> void {
                // msg 是收到的数据盒子
                // 把数据盒子翻译成文字，写到告示牌上
                label_->setText(get_qstr_from_msg(msg));
            });

        // 先写点初始内容在告示牌上（防止一开始是空白）
        label_->setText(get_qstr_from_msg(std::make_shared<SystemStatus>()));

        // 把告示牌挂出去（显示窗口）
        label_->show();
    };

    // ========================================================
    // 这个函数是“翻译员”：
    // 把 ROS 2 的数据盒子（msg）翻译成一段人类能看懂的文字
    // 返回类型是 QString，是 Qt 里的字符串类型
    // ========================================================
    QString get_qstr_from_msg(const SystemStatus::SharedPtr msg)
    {
        // 拿一张空白纸（stringstream 可以往里面拼字符串）
        std::stringstream show_str;

        // 把数据盒子里的内容，一条条写到纸上
        // msg->stamp.sec       是盒子里的“时间（秒）”
        // msg->host_name       是盒子里的“主机名”
        // msg->cpu_percent     是盒子里的“CPU 使用率”
        // msg->memory_percent  是盒子里的“内存使用率”
        // msg->memory_total    是盒子里的“内存总大小”
        // msg->memory_available是盒子里的“剩余有效内存”
        // msg->net_sent        是盒子里的“网络发送量”
        // msg->net_recv        是盒子里的“网络接收量”
        show_str << "===========新提供状态可视化显示工具===========\n"
                 << "数 据 时 间:\t" << msg->stamp.sec << "\ts\n"
                 << "主 机 名 字:\t" << msg->host_name << "\t\n"
                 << "CPU 使用率:\t" << msg->cpu_percent << "\t%\n"
                 << "内存使用率:\t" << msg->memory_percent << "\t%\n"
                 << "内存总大小:\t" << msg->memory_total << "\tMB\n"
                 << "剩余有效内存:\t" << msg->memory_available << "\tMB\n"
                 << "网络发送量:\t" << msg->net_sent << "\tMB\n"
                 << "网络接受量:\t" << msg->net_recv << "\tMB\n"
                 << "==============================================";

        // 把写好的纸转换成 Qt 能看的格式，然后交给告示牌
        return QString::fromStdString(show_str.str());
    };
};

// ============================================================
// 第四部分：厂长启动整个工厂
// main 是 C++ 程序的入口，程序从这里开始运行
// ============================================================
int main(int argc, char *argv[])
{
    // 按下 ROS 2 的总开关
    rclcpp::init(argc, argv);

    // 按下 Qt 界面的总开关
    QApplication app(argc, argv);

    // 让服务员上岗（创建一个 SysStatusDisplay 对象）
    auto node = std::make_shared<SysStatusDisplay>();

    // 开一个独立的小房间，让服务员在里面专心等数据
    // 因为等数据会一直卡住，不能和界面显示挤在一起
    std::thread spin_thread([&]() -> void {
        // 服务员开始不停等数据（这个函数会一直循环，不会返回）
        rclcpp::spin(node);
    });

    // 让这个小房间独立运行，不阻塞主线程
    spin_thread.detach();

    // 主大厅开始营业：显示窗口，等待用户操作
    // 这个函数也会一直循环，直到窗口被关闭
    app.exec();

    // 程序正常结束
    return 0;
}