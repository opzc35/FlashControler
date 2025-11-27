"""
通信协议定义
定义客户端和服务端之间的通信格式
"""
import json
import struct

class Protocol:
    """网络通信协议"""

    # 消息类型
    MSG_TERMINAL_INPUT = 1    # 终端输入
    MSG_TERMINAL_OUTPUT = 2   # 终端输出
    MSG_FILE_UPLOAD = 3       # 文件上传
    MSG_FILE_DATA = 4         # 文件数据
    MSG_FILE_COMPLETE = 5     # 文件传输完成
    MSG_HEARTBEAT = 6         # 心跳包
    MSG_AUTH = 7              # 认证
    MSG_UPDATE_CHECK = 8      # 检查更新
    MSG_UPDATE_INFO = 9       # 更新信息
    MSG_ERROR = 99            # 错误消息

    @staticmethod
    def pack_message(msg_type, data):
        """
        打包消息
        格式: [4字节长度][1字节类型][数据]
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        elif isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
        elif not isinstance(data, bytes):
            data = str(data).encode('utf-8')

        msg_len = len(data) + 1  # +1 for msg_type
        header = struct.pack('!IB', msg_len, msg_type)
        return header + data

    @staticmethod
    def unpack_message(data):
        """
        解包消息
        返回: (msg_type, payload)
        """
        if len(data) < 5:
            return None, None

        msg_len, msg_type = struct.unpack('!IB', data[:5])
        payload = data[5:5+msg_len-1]

        # 尝试解析为JSON
        try:
            payload = json.loads(payload.decode('utf-8'))
        except:
            try:
                payload = payload.decode('utf-8')
            except:
                pass  # 保持为bytes

        return msg_type, payload

    @staticmethod
    def receive_message(sock):
        """
        从socket接收完整消息
        """
        # 先接收头部（5字节）
        header = b''
        while len(header) < 5:
            chunk = sock.recv(5 - len(header))
            if not chunk:
                return None, None
            header += chunk

        msg_len, msg_type = struct.unpack('!IB', header)

        # 接收数据部分
        payload = b''
        remaining = msg_len - 1
        while len(payload) < remaining:
            chunk = sock.recv(min(remaining - len(payload), 8192))
            if not chunk:
                return None, None
            payload += chunk

        # 尝试解析payload
        try:
            payload = json.loads(payload.decode('utf-8'))
        except:
            try:
                payload = payload.decode('utf-8')
            except:
                pass  # 保持为bytes

        return msg_type, payload
