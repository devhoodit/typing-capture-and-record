import os
os.system('ffmpeg -r 60 -i "./images/%d.jpg" -vcodec mpeg4 -s 1920x1080 -b 9000k -y output.mp4')