import moviepy
from moviepy.editor import VideoFileClip


def get_video_size(input_path):
    # 加载视频
    clip = VideoFileClip(input_path)

    # 获取视频尺寸
    video_width, video_height = clip.size
    return video_width, video_height

# 使用示例
input_video_path = "D:/税务师/税法1/良善/01第一章税收基本原理/第1节第一章税法基本原理（上）2.23.mp4"
video_width, video_height = get_video_size(input_video_path)
print(f"视频宽度: {video_width}, 视频高度: {video_height}")

def trim_and_crop_video(input_path, output_path, crop_width, crop_height_top, crop_height_bottom):
    # 加载视频
    clip = VideoFileClip(input_path)

    # 获取视频总时长
    duration = clip.duration

    # 去掉前30秒和后30秒
    trimmed_clip = clip.subclip(30, max(0, duration - 30))

    # 获取视频宽度和高度
    video_width, video_height = trimmed_clip.size

    # 计算新的裁剪尺寸
    x1 = 0
    y1 = crop_height_top
    x2 = video_width - crop_width
    y2 = video_height - crop_height_bottom

    # 剪裁视频
    cropped_clip = trimmed_clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)

    # 保存处理后的视频
    cropped_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

# 使用示例
input_video_path = "input_video.mp4"
output_video_path = "output_video.mp4"
crop_width = 100  # 剪裁右边100像素
crop_height_top = 50  # 剪裁上面50像素
crop_height_bottom = 50  # 剪裁下面50像素

#trim_and_crop_video(input_video_path, output_video_path, crop_width, crop_height_top, crop_height_bottom)