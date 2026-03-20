import os
import requests

os.makedirs('static', exist_ok=True)
urls = {
    'index.html': 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzY5NDMxN2NhNTQyMzRmYjA5Njg1NjQ5YTdlOWQxYmVkEgsSBxCc7-vFiQ4YAZIBJAoKcHJvamVjdF9pZBIWQhQxNzkyNzAwNDc3Nzc3OTU3MTUzMA&filename=&opi=89354086',
    'analyze.html': 'https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzIwZWUwNDhhNTIxZDRjZTg5MDE2ZTdhOTA5ZTc5ODcxEgsSBxCc7-vFiQ4YAZIBJAoKcHJvamVjdF9pZBIWQhQxNzkyNzAwNDc3Nzc3OTU3MTUzMA&filename=&opi=89354086'
}

for name, url in urls.items():
    r = requests.get(url)
    with open(os.path.join('static', name), 'wb') as f:
        f.write(r.content)
