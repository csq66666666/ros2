# -*- coding: utf-8 -*-
"""生成三个文件的【函数调用关系图】——区分"手动调用"与"框架自动调用" """
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.font_manager import FontProperties

REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
F = FontProperties(fname=REG)
FB = FontProperties(fname=BLD)

OUT = '/home/csq/ros2/3/docs/call_graph.png'
os.makedirs(os.path.dirname(OUT), exist_ok=True)

fig = plt.figure(figsize=(24, 17), dpi=130)
fig.patch.set_facecolor('white')
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 104)
ax.axis('off')

BLUE = '#1f6feb'      # 手动调用
RED = '#d9534f'       # 框架 / Python 自动调用
GREEN = '#2f9e44'


def box(x0, y0, x1, y1, title=None, body=None, fc='#ffffff', ec='#333333',
        lw=1.6, ts=10.5, bs=8.2, rad=0.9, tcol='#111111', bcol='#252525',
        ls='solid', align='left', tls=None):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                                boxstyle="round,pad=0,rounding_size=%s" % rad,
                                linewidth=lw, edgecolor=ec, facecolor=fc,
                                linestyle=(tls or ls), mutation_aspect=1, zorder=2))
    if title:
        ax.text((x0 + x1) / 2.0, y1 - 1.5, title, ha='center', va='center',
                fontsize=ts, color=tcol, zorder=3, fontproperties=FB)
    if body:
        if align == 'left':
            ax.text(x0 + 1.4, (y0 + y1 - (2.6 if title else 0)) / 2.0, body,
                    ha='left', va='center', fontsize=bs, color=bcol,
                    linespacing=1.5, zorder=3, fontproperties=F)
        else:
            ax.text((x0 + x1) / 2.0, (y0 + y1 - (2.6 if title else 0)) / 2.0, body,
                    ha='center', va='center', fontsize=bs, color=bcol,
                    linespacing=1.5, zorder=3, fontproperties=F)


def band(x0, y0, x1, y1, fc, ec, lw=2.2, ls='solid', rad=1.2, z=1):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                                boxstyle="round,pad=0,rounding_size=%s" % rad,
                                linewidth=lw, edgecolor=ec, facecolor=fc,
                                linestyle=ls, mutation_aspect=1, zorder=z))


def arrow(p0, p1, color=BLUE, lw=2.4, ls='solid', z=4, ms=20):
    ax.annotate('', xy=p1, xytext=p0, zorder=z,
                arrowprops=dict(arrowstyle='-|>', color=color, lw=lw,
                                linestyle=ls, shrinkA=1.0, shrinkB=1.0,
                                mutation_scale=ms, connectionstyle="arc3,rad=0"))


def txt(x, y, s, fs=9, color='#333333', bold=False, ha='center', va='center',
        rot=0, z=5, ls=1.5):
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color, rotation=rot,
            linespacing=ls, zorder=z, fontproperties=(FB if bold else F))


# ═══════════════════ 标题 + 图例说明 ═══════════════════
txt(50, 102.4, 'ROS 2 人脸检测 · 函数调用关系图（谁调用谁）', fs=19, bold=True, color='#1a1a1a')
txt(50, 99.7, '蓝实线 = 你在代码里亲手写的调用（能在 .py 里搜到这一行）　｜　'
              '红虚线 = 别人自动调用你（你在代码里搜不到这一行）', fs=11, color='#5a6270')

# ═══════════════════ 入口层 ═══════════════════
band(1, 87, 99, 98, '#f4f6fa', '#b9c2d4')
txt(2.8, 96.4, '① 入口层 —— 你在终端敲的命令，最终变成对 main() 的一次调用（这一步是 setuptools 生成的脚本干的，属于"自动调用"）',
    fs=11.5, bold=True, color='#2c3e57', ha='left')

box(3, 88.5, 30, 95, 'ros2 run demo_python_service\nlearn_face_detect',
    '↓ 入口脚本自动调用\nlearn_face_detect.py 的 main()',
    fc='#ffffff', ec='#7a8aa8', ts=10, bs=8.6, align='center')
box(32.5, 88.5, 61, 95, 'ros2 run demo_python_service\nface_detect_node',
    '↓ 入口脚本自动调用\nface_detect_node.py 的 main()',
    fc='#ffffff', ec='#7a8aa8', ts=10, bs=8.6, align='center')
box(71, 88.5, 97.5, 95, 'ros2 run demo_python_service\nface_detect_client_node',
    '↓ 入口脚本自动调用\n客户端 main()',
    fc='#ffffff', ec='#7a8aa8', ts=10, bs=8.6, align='center')

for x, xc in ((15.5, 16.5), (46.5, 46.75), (84.5, 84.25)):
    arrow((xc, 88.5), (xc, 86.2), color=RED, lw=2.6, ls='dashed')

# ═══════════════════ 三条列 ═══════════════════
band(1, 8, 30, 86, '#eef6ff', '#6ea8dc')
band(31.5, 8, 61, 86, '#f2fbf3', '#6fbf83')
band(71, 8, 99, 86, '#fff8ec', '#d99b3a')

# ---------- 列 1：learn_face_detect.py ----------
txt(2.6, 84.4, 'learn_face_detect.py', fs=13, bold=True, color='#1d4e79', ha='left')
txt(2.6, 82.1, '单机版 · 整个文件只有 1 个函数', fs=9.5, color='#5a7fa0', ha='left')

box(3, 58, 28, 80.5, 'def main()', '''拿图片路径
  ▶ get_package_share_directory('demo_python_service')
  ▶ os.path.join(..., 'resource', 'default.jpg')

读图 + 检测
  ▶ image = cv2.imread(default_image_path)
  ▶ face_locations = face_recognition.face_locations(
        image, number_of_times_to_upsample=1, model='hog')

画框（对检测出的每一张脸循环）
  ▶ for top,right,bottom,left in face_locations:
        cv2.rectangle(image, (left,top), (right,bottom), (0,255,0), 4)

显示
  ▶ cv2.imshow("Face Detection Result", image)
  ▶ cv2.waitKey(0)      ← 不加这句窗口一闪而过''', ec='#6ea8dc', ts=11)

box(3, 36, 28, 57, '★ 这个文件的调用关系最简单', '''【为什么简单】
· 没有 class、没有 self、没有回调函数
· 从头到尾是一条直线，跑完就退出
· 上面每一个 ▶ 都是你自己写的调用（蓝线）

【它和 ROS 的关系】
· 只用了一件事：get_package_share_directory
  去 install/ 里把图片找出来
· 不通信、不发布、不订阅、不提供服务

【谁调用它】
· 只有入口脚本会调用 main()，没有第二个调用者
· 检测和画框都在同一个进程里完成''',
    fc='#ffffff', ec='#6ea8dc', ts=10.5)

box(3, 9, 28, 32, '⚠ 这个文件少了一行（建议补上）', '''文件里只有 def main(): 这个"定义"，
没有写"调用"它的语句。补在文件最后：

    if __name__ == '__main__':
        main()

【为什么 ros2 run 却能跑】
   入口脚本就是上面那两行的等价物，
   由 setuptools 按 setup.py 的 entry_points
   自动生成，所以它能替你调用 main()。

【自己验证一下】
   python3 learn_face_detect.py  → 没有任何反应
   ros2 run ... learn_face_detect → 弹窗''',
    fc='#fff1f0', ec='#c96a63', ls='dashed', ts=10.5, bcol='#7a3b36')

# ---------- 列 2：face_detect_node.py（服务端） ----------
txt(33.1, 84.4, 'face_detect_node.py', fs=13, bold=True, color='#1f5c33', ha='left')
txt(33.1, 82.1, '服务端 · 3 个函数', fs=9.5, color='#4a7d5c', ha='left')

box(35, 69, 59.5, 80.5, 'def main(args=None)', '''  ▶ rclpy.init(args=args)
  ▶ node = FaceDetectNode()    ← 触发 __init__
  ▶ rclpy.spin(node)           ← 卡住不返回
  ▶ node.destroy_node()
  ▶ rclpy.shutdown()''', ec='#6fbf83', ts=11, bs=8.0)

box(35, 53, 59.5, 67.5, 'def __init__(self)   ← Python 自动调用', '''  ▶ super().__init__('face_detect_node')
  ▶ self.create_service(FaceDetector, 'face_detect',
                        self.face_detect_callback)      ★
  ▶ self.bridge = CvBridge()
  ▶ self.default_image_path = os.path.join(
        get_package_share_directory('demo_python_service'),
        'resource', 'default.jpg')
  ▶ self.get_logger().info('Face Detect Service is ready.')''',
    ec='#6fbf83', ts=10, bs=8.0)

box(35, 22, 59.5, 50,
    'def face_detect_callback(request, response)   ← ★ rclpy 自动调用',
    '''★ 全项目唯一被"框架"调用的函数：
  你的代码从没写过 face_detect_callback(...)，
  是 rclpy.spin() 收到 /face_detect 请求时替你调的。
────────────────────────────────────
  ▶ if request.image.data:
        cv_image = self.bridge.imgmsg_to_cv2(request.image,'bgr8')
    else:
        cv_image = cv2.imread(self.default_image_path)
  ▶ start_time = time.time()
  ▶ face_locations = face_recognition.face_locations(
        cv_image, number_of_times_to_upsample=1, model='hog')
  ▶ response.use_time = time.time() - start_time
  ▶ response.number = len(face_locations)
  ▶ for top,right,bottom,left in face_locations:
        response.top.append(top) / right / bottom / left
  ▶ return response   ← 返回值被 rclpy 打包发回客户端''',
    ec='#3f9a5c', lw=2.8, ts=10, bs=8.0)

box(35, 9.5, 59.5, 19, None,
    '★ 一句话记住：\n'
    'main / __init__ 是"你自己走流程"；\n'
    'callback 是"别人按门铃叫你"。',
    fc='#fffbeb', ec='#d9a520', ls='dashed', bs=8.6, bcol='#8a6410', align='center')

# main → __init__
arrow((47, 69), (47, 67.5), color=BLUE, lw=2.4)
txt(52.5, 68.2, 'FaceDetectNode()', fs=7.2, color=BLUE)

# rclpy.spin  →  callback（框架自动调用，绕左侧走廊下来）
arrow((33.6, 72), (33.6, 47), color=RED, lw=2.6, ls='dashed')
arrow((33.6, 47), (35, 47), color=RED, lw=2.6, ls='dashed')
txt(32.6, 60, 'rclpy.spin() 收到请求 → 自动调用 callback', fs=8,
    color=RED, bold=True, rot=90)

# ---------- 列 3：face_detect_client_node.py（客户端） ----------
txt(72.1, 84.4, 'face_detect_client_node.py', fs=13, bold=True, color='#8a5a12', ha='left')
txt(72.1, 82.1, '客户端 · 4 个函数', fs=9.5, color='#a07a3a', ha='left')

box(73, 70, 97, 80.5, 'def main(args=None)', '''  ▶ rclpy.init(args=args)
  ▶ node = FaceDetectClientNode()  ← 触发 __init__
  ▶ node.send_request()            ← 全部活在这
  ▶ node.destroy_node() / rclpy.shutdown()''',
    ec='#d99b3a', ts=11, bs=8.0)

box(73, 54, 97, 67.5, 'def __init__(self)   ← Python 自动调用', '''  ▶ super().__init__('face_detect_client_node')
  ▶ self.create_client(FaceDetector, 'face_detect')   ★
  ▶ self.bridge = CvBridge()
  ▶ self.image = cv2.imread(os.path.join(
        get_package_share_directory('demo_python_service'),
        'resource', '2026-10-02_14-13.png'))
  ▶ self.get_logger().info('客户端启动')''',
    ec='#d99b3a', ts=10, bs=8.0)

box(73, 31, 97, 51, 'def send_request(self)', '''  ▶ while not self.client.wait_for_service(timeout_sec=1.0):
        self.get_logger().info('服务未就绪，等待中...')
  ▶ request = FaceDetector.Request()
  ▶ request.image = self.bridge.cv2_to_imgmsg(self.image,'bgr8')
  ▶ future = self.client.call_async(request)       ★ 下单拿号
  ▶ rclpy.spin_until_future_complete(self, future) ★ 盯号等餐
  ▶ response = future.result()
  ▶ self.get_logger().info(f'人脸检测结果: {response.number} ...')
  ▶ self.show_response(response)''',
    ec='#d99b3a', ts=11, bs=8.0)

box(73, 17, 97, 28.5, 'def show_response(self, response)', '''  ▶ for i in range(response.number):
        cv2.rectangle(self.image, (left,top), (right,bottom),
                      (255,0,0), 4)
  ▶ cv2.imshow('Face Detection Result', self.image)
  ▶ cv2.waitKey(0)''', ec='#d99b3a', ts=10, bs=8.0)

box(73, 9.5, 97, 15.2, None,
    '★ 客户端 4 个函数全是"你自己调用"的，没有任何框架回调。',
    fc='#fffbeb', ec='#d9a520', ls='dashed', bs=8.4, bcol='#8a6410', align='center')

# main → __init__
arrow((85, 70), (85, 67.5), color=BLUE, lw=2.4)
txt(91.5, 68.2, 'FaceDetectClientNode()', fs=7.2, color=BLUE)
# main → send_request（绕左侧走廊）
arrow((74, 73.5), (72, 73.5), color=BLUE, lw=2.2)
arrow((72, 73.5), (72, 41), color=BLUE, lw=2.2)
arrow((72, 41), (74, 41), color=BLUE, lw=2.2)
txt(85, 52.4, 'node.send_request()', fs=7.2, color=BLUE)
# send_request → show_response
arrow((85, 31), (85, 28.5), color=BLUE, lw=2.4)
txt(90.5, 29.7, 'self.show_response(response)', fs=7.2, color=BLUE)

# ---------- 中间：跨进程 ----------
band(61.3, 26, 70.7, 58, '#fff5f5', RED, lw=1.8, ls='dashed')
txt(66, 55.5, '/face_detect', fs=9.5, bold=True, color='#8a2b28')
txt(66, 53.0, '跨进程服务调用', fs=7.6, color='#8a2b28')
arrow((72, 45), (59.5, 45), color=RED, lw=2.8)
txt(66, 47.2, 'request：整张图', fs=7.2, color=RED)
arrow((59.5, 37), (72, 37), color=GREEN, lw=2.8)
txt(66, 34.8, 'response：坐标', fs=7.2, color=GREEN)
txt(66, 30.5, '这两次"送达"\n都是 rclpy 干的', fs=7.2, color='#8a2b28')

# ═══════════════════ 图例 ═══════════════════
band(1, 0.5, 99, 6.6, '#f8f8fa', '#c8ccd8')
txt(2.8, 5.2, '图例', fs=11, bold=True, color='#333333', ha='left')
arrow((8, 3.6), (13, 3.6), color=BLUE, lw=2.6)
txt(14, 3.6, '你手动写的调用：代码里能搜到这一行（例如 cv2.imread(...)、self.create_service(...)）',
    fs=9, color='#333333', ha='left')
arrow((58, 3.6), (63, 3.6), color=RED, lw=2.6, ls='dashed')
txt(64, 3.6, '框架 / Python 自动调用你：代码里搜不到这一行（main、__init__、face_detect_callback）',
    fs=9, color='#333333', ha='left')

fig.savefig(OUT, facecolor='white')
print('saved:', OUT)
