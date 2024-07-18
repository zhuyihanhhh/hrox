import os
import re

file_path = r'/ybs-ep18.hrox'

output_file_path = r'C:\Users\zhuyihan\Desktop\hrox_reader\clip_list.txt'
# 读取文件内容
with open(file_path, 'r', encoding='utf-8') as file:
    file_content = file.read()

# 匹配所有clip路径
clip_pattern = re.compile(r'file="([^"]+)"')

clip_paths = clip_pattern.findall(file_content)

# for i in clip_paths:
#     dir_name = os.path.dirname(i)
#     if os.path.exists(dir_name):
#         if ".dpx" in i:
#             dir_path = os.path.dirname(i)
#             print(dir_path)
#             # print(i)
#         else:
#             print(i)

# 将所有clip路径保存到输出文件
with open(output_file_path, 'w', encoding='utf-8') as f:
    for i in clip_paths:
        dir_name = os.path.dirname(i)
        if os.path.exists(dir_name):
            if ".dpx" in i:
                dir_path = os.path.dirname(i)
                # print(dir_path)
                f.write(dir_path + '\n')
            else:
                f.write(i + '\n')
