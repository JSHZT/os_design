"""
- Block: 磁盘中的物理块
- FAT: Fat表
- FCB: 目录项
- CatalogNode: 目录树结点
"""
blockSize = 512
blockNum = 512


class Block:
    def __init__(self, blockIndex, data=""):
        self.blockIndex = blockIndex
        self.data = data

    # 写单个块
    def write(self, newData: str):
        self.data = newData[:blockSize]
        return newData[blockSize:]

    def read(self):
        return self.data

    def isFull(self):
        return len(self.data) == blockSize

    # 追加新内容，返回无法写入的部分
    def append(self, newData: str) -> str:
        remainSpace = blockSize-len(self.data)
        if remainSpace >= newData:
            # self.data+=newData
            return ""
        else:
            self.data += newData[:remainSpace]
            return newData[remainSpace:]

    def clear(self):
        self.data = ""


class FAT:
    # -1为文件结尾的意思，-2为空盘块，其他数字为指向下一盘块
    def __init__(self):
        self.fat = []
        for _ in range(blockNum):
            self.fat.append(-2)

    def findBlank(self):
        for i in range(blockNum):
            if self.fat[i] == -2:
                return i
        return -1

    def write(self, data: str, disk):
        start, cur = -1, -1
        while data != "":
            newLoc = self.findBlank()
            if newLoc == -1:
                raise Exception(print('磁盘空间不足!'))
            if cur != -1:
                self.fat[cur] = newLoc
            else:
                start = newLoc
            cur = newLoc
            data = disk[cur].write(data)
            self.fat[cur] = -1
        return start

    def delete(self, start, disk):
        if start == -1:
            return
        while self.fat[start] != -1:
            disk[start].clear()
            las = self.fat[start]
            self.fat[start] = -2
            start = las
        self.fat[start] = -2
        disk[start].clear()

    def update(self, start, data, disk):
        """
        清空以start开始的fat表以及磁盘空间
        然后再重新写入
        """
        self.delete(start, disk)
        return self.write(data, disk)

    def read(self, start, disk):
        """
        读取从start开始的文件内容
        """
        data = ""
        while self.fat[start] != -1:
            data += disk[start].read()
            start = self.fat[start]
        data += disk[start].read()
        return data

    def check_free(self, disk):
        count = 0
        count_ = 0
        for i in range(len(self.fat)):
            if self.fat[i] == -2:
                count += 1
            elif self.fat[i] == -1:
                count_ += blockSize - len(disk[i].data)
        return count * 512 +count_
    
class FCB:
    def __init__(self, name, createTime, data, fat, disk):
        self.name = name
        self.createTime = createTime
        # 最后修改时间
        self.updateTime = self.createTime

        # 根据data为其分配空间
        self.start = - 1

    def update(self, newData, fat, disk):
        """
        更新文件内容
        """
        self.start = fat.update(self.start, newData, disk)

    def delete(self, fat, disk):
        fat.delete(self.start, disk)

    def read(self, fat, disk):
        if self.start == -1:
            return ""
        else:
            return fat.read(self.start, disk)


class CatalogNode:
    def __init__(self, name, isFile, fat, disk, createTime, parent=None, data=""):
        self.name = name  # 路径名
        self.isFile = isFile
        self.parent = parent
        self.createTime = createTime
        self.updateTime = self.createTime
        self.owner = ''
        self.permission_group = []
        if not self.isFile:
            self.children = []  # 文件夹
        else:
            self.data = FCB(name, createTime, data, fat, disk)
