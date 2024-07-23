from applications.common.str_enum import StrEnum


class cmd(StrEnum):
    爬取商品 = '爬取商品'
    删除商品 = '删除商品'
    发布商品 = '发布商品'
    下架商品 = '下架商品'
    重新上架 = '重新上架'
    商品降价 = '商品降价'
    开启闲鱼币抵扣 = '开启闲鱼币抵扣'

    # todo 定时 生成 签到 一键擦亮任务
    # 一键擦亮 = '一键擦亮'
    # 签到闲鱼币 = '签到闲鱼币'


# 这些 cmd 的 cmd_args 中 有 ProductToDevice 的 id, 用于任务执行前/后 更新状态 等操作
group_p2d_cmd = [
    cmd.删除商品,
    cmd.发布商品,
    cmd.下架商品,
    cmd.重新上架,
    cmd.商品降价,
]


class cmd_state(StrEnum):
    执行成功 = '执行成功'

    执行失败 = '执行失败'
    次数用尽 = '次数用尽'
    执行超时 = '执行超时'

    运行中 = '运行中'
    重试中 = '重试中'

    未运行 = '未运行'


