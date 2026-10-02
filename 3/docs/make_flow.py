# -*- coding: utf-8 -*-
"""生成 demo_python_service 三个文件的协作流程图"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
BLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
F = dict(fontproperties=__import__('matplotlib.font_manager', fromlist=['FontProperties']).FontProperties(fname=REG))
FB = dict(fontproperties=__import__('matplotlib.font_manager', fromlist=['FontProperties']).FontProperties(fname=BLD))

OUT = '/home/csq/ros2/3/docs/face_detect_flow.png'
os.makedirs(os.path.dirname(OUT), exist_ok=True)

fig = plt.figure(figsize=(23, 16), dpi=130)
fig.patch.set_facecolor('white')
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 104)
ax.axis('off')


def box(x0, y0, x1, y1, title=None, body=None, fc='#ffffff', ec='#333333',
        lw=1.6, ts=11.5, bs=9.5, rad=0.9, tcol='#111111', bcol='#252525', ls='solid'):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                                boxstyle="round,pad=0,rounding_size=%s" % rad,
                                linewidth=lw, edgecolor=ec, facecolor=fc,
                                linestyle=ls, mutation_aspect=1, zorder=2))
    cx = (x0 + x1) / 2.0
    if title and body:
        ax.text(cx, y1 - 1.5, title, ha='center', va='center', fontsize=ts,
                color=tcol, zorder=3, **FB)
        ax.text(cx, (y0 + y1 - 2.6) / 2.0, body, ha='center', va='center', fontsize=bs,
                color=bcol, linespacing=1.5, zorder=3, **F)
    elif title:
        ax.text(cx, (y0 + y1) / 2.0, title, ha='center', va='center', fontsize=ts,
                color=tcol, zorder=3, **FB)
    else:
        ax.text(cx, (y0 + y1) / 2.0, body, ha='center', va='center', fontsize=bs,
                color=bcol, linespacing=1.55, zorder=3, **F)


def band(x0, y0, x1, y1, fc, ec, lw=2.2, ls='solid', z=1):
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                                boxstyle="round,pad=0,rounding_size=1.2",
                                linewidth=lw, edgecolor=ec, facecolor=fc,
                                linestyle=ls, mutation_aspect=1, zorder=z))


def arrow(p0, p1, color='#444444', lw=2.4, rad=0.0, ls='solid', z=4):
    ax.annotate('', xy=p1, xytext=p0, zorder=z,
                arrowprops=dict(arrowstyle='-|>', color=color, lw=lw,
                                linestyle=ls, shrinkA=1.5, shrinkB=1.5,
                                mutation_scale=20,
                                connectionstyle="arc3,rad=%s" % rad))


def label(x, y, s, fs=10, color='#333333', bold=False, ha='center', va='center', z=5):
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color, linespacing=1.5,
            zorder=z, **(FB if bold else F))


# ══════════════ 标题 ══════════════
label(50, 102.4, 'ROS 2 人脸检测 · 三个文件的协作关系', fs=19, bold=True, color='#1a1a1a')
label(50, 99.6, 'demo_python_service 包 ｜ 1 个单机练习文件 + 1 个服务端 + 1 个客户端 ｜ 服务接口来自 chapt4_interfaces',
      fs=11, color='#5a6270')

# ══════════════ ① 编译期 ══════════════
band(1, 84, 99, 98.2, '#f4f6fa', '#b9c2d4')
label(2.8, 96.8, '① 编译期 · colcon build —— 三个 .py 先被"装"成命令和资源，ros2 run 才找得到它们',
      fs=12.5, bold=True, color='#2c3e57', ha='left')

box(3, 88.2, 34, 95.7, 'setup.py · entry_points',
    'learn_face_detect\nface_detect_node\nface_detect_client_node\n→ 注册 3 个 ros2 run 命令',
    fc='#ffffff', ec='#7a8aa8', ts=10.5, bs=9)
box(36, 88.2, 67, 95.7, 'setup.py · data_files',
    'resource/default.jpg\nresource/2026-10-02_14-13.png\n→ 拷进 install/.../share/\n   demo_python_service/resource/',
    fc='#ffffff', ec='#7a8aa8', ts=10.5, bs=9)
box(69, 88.2, 97, 95.7, 'chapt4_interfaces（另一个包）',
    'srv/FaceDetector.srv\n→ 生成 Python 类 FaceDetector\n   含 Request 与 Response\n（服务端和客户端都 import 它）',
    fc='#ffffff', ec='#7a8aa8', ts=10.5, bs=9)

box(3, 84.4, 97, 87.4, None,
    'colcon build  →  install/demo_python_service/{ lib/python3.10/site-packages/demo_python_service/ , '
    'share/demo_python_service/resource/ }   +   install/chapt4_interfaces/',
    fc='#e8edf6', ec='#7a8aa8', bs=10)

for x in (18.5, 51.5, 83.0):
    arrow((x, 88.2), (x, 87.4), color='#7a8aa8', lw=2)
arrow((50, 84.4), (50, 82.0), color='#7a8aa8', lw=2.6)

# ══════════════ ② 单机版 ══════════════
band(1, 63, 99, 82, '#eef6ff', '#6ea8dc')
label(2.8, 80.3, '② 单机版 · learn_face_detect.py —— 完全不碰 ROS，检测和显示都在同一个进程里',
      fs=12.5, bold=True, color='#1d4e79', ha='left')

box(3, 67, 17, 78.5, '① 定位图片',
    'get_package_share_directory\n+ os.path.join\n→ install/.../resource/\n   default.jpg', ec='#6ea8dc', ts=10.5, bs=8.8)
box(19, 67, 32, 78.5, '② cv2.imread',
    '读成 numpy\n数组 (BGR)\n失败会返回\nNone 不报错', ec='#6ea8dc', ts=10.5, bs=8.8)
box(34, 67, 54, 78.5, '③ 核心检测',
    'face_recognition\n  .face_locations(\n     upsample=1,\n     model="hog")\n→ [(top,right,bottom,left)...]', ec='#2f7dc0', lw=2.6, ts=10.5, bs=8.8)
box(56, 67, 70, 78.5, '④ cv2.rectangle',
    'for 循环逐张\n画绿框\n(0,255,0)\n线宽 4', ec='#6ea8dc', ts=10.5, bs=8.8)
box(72, 67, 86, 78.5, '⑤ cv2.imshow',
    '+ cv2.waitKey(0)\n弹窗显示结果\n不加 waitKey\n窗口会一闪而过', ec='#6ea8dc', ts=10.5, bs=8.8)
box(88, 67, 97.5, 78.5, None,
    '纯单机\n没有 rclpy\n没有 cv_bridge\n没有服务', fc='#fffbeb', ec='#d9a520', ls='dashed', bs=9, bcol='#8a6410')

for a, b in [(17, 19), (32, 34), (54, 56), (70, 72), (86, 88)]:
    arrow((a, 72.7), (b, 72.7), color='#2f7dc0', lw=2.2)

label(2.8, 65.1, '★ 关键：核心检测就是一句 face_recognition.face_locations() —— 它只是本进程内的普通函数调用，跟 ROS 一点关系都没有。',
      fs=10.5, color='#1d4e79', ha='left')

label(50, 61.6, '↓  理解原理之后，把这份"检测能力"包装成 ROS 2 服务，让别的节点也能远程调用  ↓',
      fs=11.5, bold=True, color='#2a6b3f')

# ══════════════ ③ 服务版 ══════════════
band(1, 9, 99, 60, '#f2fbf3', '#6fbf83')
label(2.8, 58.3, '③ 服务版 · face_detect_node.py（服务端）  ↔  face_detect_client_node.py（客户端）—— 两个进程通过 /face_detect 服务通信',
      fs=12.5, bold=True, color='#1f5c33', ha='left')

# ---- 客户端列 ----
box(3, 48, 38, 56.5, 'main()',
    "rclpy.init → FaceDetectClientNode() → node.send_request()\n→ destroy_node() → rclpy.shutdown()",
    fc='#fff8ec', ec='#d99b3a', ts=11, bs=9)
box(3, 37.5, 38, 46.5, '__init__()',
    "super().__init__('face_detect_client_node')\nself.create_client(FaceDetector, 'face_detect')\nself.bridge = CvBridge()\ncv2.imread('2026-10-02_14-13.png')  ← 要发的图",
    fc='#fff8ec', ec='#d99b3a', ts=11, bs=9)
box(3, 19.5, 38, 35.5, 'send_request()',
    "① while not wait_for_service(1.0): 打日志继续等\n② request.image = bridge.cv2_to_imgmsg(\n        self.image, encoding='bgr8')\n③ future = self.client.call_async(request)\n④ spin_until_future_complete(self, future)\n⑤ response = future.result()\n→ 交给 show_response()",
    fc='#fff8ec', ec='#d99b3a', ts=11, bs=8.8)
box(3, 10.5, 38, 17.5, 'show_response(response)',
    "⑥ for i in range(response.number):\n     cv2.rectangle(..., (255,0,0), 4)   画蓝框\n⑦ cv2.imshow + cv2.waitKey(0)",
    fc='#fff8ec', ec='#d99b3a', ts=11, bs=8.8)

for y0, y1 in [(48, 46.5), (37.5, 35.5), (19.5, 17.5)]:
    arrow((20.5, y0), (20.5, y1), color='#d99b3a', lw=2.2)

# ---- 服务端列 ----
box(60, 48, 97, 56.5, 'main()',
    "rclpy.init → FaceDetectNode() → rclpy.spin(node)   常驻等待请求\nCtrl+C → destroy_node() → rclpy.shutdown()",
    fc='#eaf7ee', ec='#3f9a5c', ts=11, bs=9)
box(60, 37.5, 97, 46.5, '__init__()',
    "super().__init__('face_detect_node')\nself.create_service(FaceDetector, 'face_detect',\n                    self.face_detect_callback)\nself.bridge = CvBridge()   ·   拼接 default.jpg 路径",
    fc='#eaf7ee', ec='#3f9a5c', ts=11, bs=9)
box(60, 19.5, 97, 35.5, 'face_detect_callback(request, response)',
    "① request.image.data 有图？\n     bridge.imgmsg_to_cv2(request.image,'bgr8')\n   否则 cv2.imread(self.default_image_path)\n② face_recognition.face_locations(\n        cv_image, upsample=1, model='hog')\n③ 填 response: use_time / number\n        / top[] right[] bottom[] left[]\n④ return response",
    fc='#eaf7ee', ec='#3f9a5c', ts=11, bs=8.8)
box(60, 10.5, 97, 17.5, '★ 关键点',
    'face_recognition 只在服务端被 import。\n客户端拿到的是"坐标数字"，它自己不会检测。',
    fc='#fffbeb', ec='#d9a520', ls='dashed', ts=11, bs=9, bcol='#8a6410')

for y0, y1 in [(48, 46.5), (37.5, 35.5), (19.5, 17.5)]:
    arrow((78.5, y0), (78.5, y1), color='#3f9a5c', lw=2.2)

# ---- 中间：服务契约 + 通信 ----
box(40, 41, 58, 52.5, '服务契约',
    '服务名：face_detect\n类型：FaceDetector\n(chapt4_interfaces/\n   srv/FaceDetector.srv)\n两端都按它编译',
    fc='#fff7e6', ec='#d9a520', lw=2.2, ts=10.5, bs=8.6, bcol='#7a5a10')

band(38.6, 18.5, 59.4, 39.5, '#eaf4ff', '#5b8fd6', lw=1.8, ls='dashed')
label(49, 37.6, 'ROS 2 服务通信（跨进程）', fs=10, bold=True, color='#1d4e79')
arrow((40.8, 30.5), (57.2, 30.5), color='#1f6feb', lw=3)
label(49, 33.0, 'request：整张图\nsensor_msgs/Image', fs=8.6, color='#1f6feb')
arrow((57.2, 23.0), (40.8, 23.0), color='#2f9e44', lw=3)
label(49, 24.6, 'response：number / use_time\n/ top[] right[] bottom[] left[]', fs=8.6, color='#2f9e44')

label(2.8, 8.9, '★ 分工：客户端负责"读图 → 转 ROS 消息 → 发请求 → 收坐标 → 画框"，服务端负责"收图 → 检测 → 回坐标"。检测这个重活只在服务端干一次。',
      fs=10.5, color='#1f5c33', ha='left')

# ══════════════ ④ 技术底座 ══════════════
band(1, 0.2, 99, 7.2, '#f8f2fc', '#b48fd0')
label(2.8, 6.0, '④ 三个文件共享的技术底座（都装在解释器 /usr/bin/python3 下）',
      fs=11.5, bold=True, color='#4d2b6b', ha='left')

box(3, 0.7, 22, 4.9, None,
    'face_recognition\n底层 dlib + face_recognition_models\n(提供 .dat 模型)   ▶ ② 与 ③服务端',
    fc='#ffffff', ec='#b48fd0', bs=8.6)
box(24, 0.7, 42, 4.9, None,
    'OpenCV · cv2\nimread / rectangle / imshow / waitKey\n▶ 三个文件都用',
    fc='#ffffff', ec='#b48fd0', bs=8.6)
box(44, 0.7, 60, 4.9, None,
    'cv_bridge\nROS Image ⇄ OpenCV 图像\n▶ ③ 服务端 + 客户端',
    fc='#ffffff', ec='#b48fd0', bs=8.6)
box(62, 0.7, 78, 4.9, None,
    'rclpy\nNode / Service / Client / spin\n▶ ③ 服务端 + 客户端',
    fc='#ffffff', ec='#b48fd0', bs=8.6)
box(80, 0.7, 96, 4.9, None,
    'ament_index_python\nget_package_share_directory\n▶ 三个文件都用',
    fc='#ffffff', ec='#b48fd0', bs=8.6)

for x in (12, 50, 88):
    arrow((x, 7.25), (x, 8.95), color='#b48fd0', lw=1.8, ls='dashed')

fig.savefig(OUT, facecolor='white')
print('saved:', OUT)
