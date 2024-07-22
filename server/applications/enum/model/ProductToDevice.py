from applications.common.str_enum import StrEnum


class publish_state(StrEnum):
    发布中 = '发布中'
    已发布 = '已发布'
    已下架 = '已下架'
