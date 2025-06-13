import requests
import os

# === 步骤一：获取上传授权信息 ===
auth_url = "http://shop-gateway.ad.tuhutest.cn:9010/int-service-arch-file-upload/Utility/RemoteUpload/GetUploadAuthorization"
params = {
    "directoryName": "lijunyi3",
    "supportHeaders": "true",
    "extensions": ".mp4",
    "type": "2"
}
headers = {
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Accept': '*/*'
}

auth_response = requests.get(auth_url, params=params, headers=headers)
print("授权响应：", auth_response.status_code)
auth_json = auth_response.json()

# === 步骤二：准备上传 ===
upload_info = auth_json["Result"]
upload_uri = upload_info["Uri"]
form_data = upload_info["Form"]
upload_headers = upload_info["Headers"]
file_key = upload_info.get("FileKey", "file")

# === 步骤三：上传文件（使用 requests）===
file_path = "../mp4/demo.mp4"  # ← 替换为你的本地视频路径

with open(file_path, 'rb') as f:
    files = {
        file_key: (os.path.basename(file_path), f, 'video/mp4')
    }

    # 注意：form_data 是 multipart 中除文件外的字段
    response = requests.post(
        upload_uri,
        headers={
            **upload_headers,
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Accept': '*/*'
        },
        data=form_data,
        files=files,
        verify=False  # ← 本地调试可以关闭 SSL 验证
    )

    print("上传响应：", response.status_code)
    print(response.text)

print("上传响应：", response.status_code)
print("响应头：", response.headers)

etag = response.headers.get("ETag")
location = response.headers.get("Location")

# === 第三步：上报上传结果 ===
report_url = "http://shop-gateway.ad.tuhutest.cn:9010/int-service-arch-file-upload/Utility/RemoteUpload/ReportUploadResult"
report_headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Accept': '*/*'
}

report_body = {
    "statusCode": response.status_code,
    "headers": [
        {"key": "ETag", "value": etag},
        {"key": "Location", "value": location}
    ]
}

report_response = requests.post(report_url, json=report_body, headers=report_headers)
print("上报响应：", report_response.status_code)
print(report_response.text)

json_data = report_response.json()
path = json_data.get("Result", {}).get("Path", None)
print("视频路径：", "https://v.tuhu.org/" + path)