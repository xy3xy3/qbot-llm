

# 使用说明

## 申请开发者

在 https://q.qq.com/ 注册

## 创建机器人

在 https://q.qq.com/#/app/bot 创建机器人

## 沙箱配置

在 https://q.qq.com/qqbot/#/developer/sandbox 设置测试的群

## 获取配置

在 https://q.qq.com/qqbot/#/developer/developer-setting 获取appid，secret，填写配置

## 填写大模型api的base_url和key

如果是国内的平台，比如智谱
```
base_url: "https://open.bigmodel.cn/api/paas/v4/"
api_key: "你的key"
```

## 运行

先修改`config.copy.yaml`为`config.yaml`，填写配置

```bash
pip install -r requirements.txt
python main.py
```
