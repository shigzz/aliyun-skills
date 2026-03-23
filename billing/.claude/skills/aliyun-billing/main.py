# -*- coding: utf-8 -*-
"""
阿里云账单查询 Skill
通过阿里云 OpenAPI 查询 DescribeInstanceBill 接口
支持分页查询所有数据
"""
import os
import sys
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

from alibabacloud_bssopenapi20171214.client import Client as BssOpenApi20171214Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_bssopenapi20171214 import models as bss_open_api_20171214_models
from alibabacloud_tea_util import models as util_models
from dotenv import load_dotenv


def check_credentials() -> bool:
    """
    检查阿里云 AK/SK 配置
    优先级：1. 环境变量 2. 工作目录下的 .env 文件
    所需变量：ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET

    Returns:
        bool: 是否成功配置凭据
    """
    # 首先检查环境变量
    access_key_id = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID')
    access_key_secret = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET')

    if access_key_id and access_key_secret:
        print("✓ 已从环境变量读取 AK/SK")
        return True

    # 尝试从工作目录下的 .env 文件加载
    env_paths = [
        '.env',
        '../.env',
        '../../.env',
        os.path.join(os.getcwd(), '.env'),
        os.path.join(os.path.dirname(__file__), '.env'),
    ]

    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
            access_key_id = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID')
            access_key_secret = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
            if access_key_id and access_key_secret:
                print(f"✓ 已从 {env_path} 文件读取 AK/SK")
                return True

    print("✗ 未找到阿里云 AK/SK 配置")
    print("  请设置以下环境变量或在项目根目录创建 .env 文件：")
    print("    - ALIBABA_CLOUD_ACCESS_KEY_ID")
    print("    - ALIBABA_CLOUD_ACCESS_KEY_SECRET")
    print("\n  .env 文件格式示例：")
    print("    ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id")
    print("    ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret")
    return False


def create_client() -> BssOpenApi20171214Client:
    """
    使用凭据初始化阿里云 BSS OpenAPI Client

    Returns:
        BssOpenApi20171214Client: 阿里云 BSS 客户端实例

    Raises:
        Exception: 初始化失败时抛出异常
    """
    credential = CredentialClient()
    config = open_api_models.Config(credential=credential)
    # Endpoint 参考 https://api.aliyun.com/product/BssOpenApi
    config.endpoint = 'business.aliyuncs.com'
    return BssOpenApi20171214Client(config)


@dataclass
class DescribeInstanceBillParams:
    """DescribeInstanceBill 接口参数"""
    billing_cycle: str                    # 账期 YYYY-MM，必填
    product_code: Optional[str] = None    # 产品代码
    product_type: Optional[str] = None    # 产品类型
    subscription_type: Optional[str] = None  # Subscription/PayAsYouGo
    is_billing_item: Optional[bool] = None   # 是否按计费项维度
    page_num: int = 1                     # 页码
    page_size: int = 100                  # 每页数量，最大300
    is_hide_zero_charge: Optional[bool] = None  # 是否隐藏0费用
    billing_date: Optional[str] = None    # 账单日期，DAILY粒度时必填
    granularity: Optional[str] = None     # MONTHLY/DAILY
    bill_owner_id: Optional[int] = None   # 资源归属账号ID


def build_request(params: DescribeInstanceBillParams) -> bss_open_api_20171214_models.DescribeInstanceBillRequest:
    """
    根据参数构建 DescribeInstanceBillRequest

    Args:
        params: 查询参数

    Returns:
        DescribeInstanceBillRequest: 阿里云 SDK 请求对象
    """
    request = bss_open_api_20171214_models.DescribeInstanceBillRequest()

    # 必填参数
    request.billing_cycle = params.billing_cycle

    # 可选参数
    if params.product_code:
        request.product_code = params.product_code
    if params.product_type:
        request.product_type = params.product_type
    if params.subscription_type:
        request.subscription_type = params.subscription_type
    if params.is_billing_item is not None:
        request.is_billing_item = params.is_billing_item
    if params.page_num:
        request.page_num = params.page_num
    if params.page_size:
        request.page_size = params.page_size
    if params.is_hide_zero_charge is not None:
        request.is_hide_zero_charge = params.is_hide_zero_charge
    if params.billing_date:
        request.billing_date = params.billing_date
    if params.granularity:
        request.granularity = params.granularity
    if params.bill_owner_id:
        request.bill_owner_id = params.bill_owner_id

    return request


def query_single_page(
    client: BssOpenApi20171214Client,
    params: DescribeInstanceBillParams
) -> Dict[str, Any]:
    """
    查询单页账单数据

    Args:
        client: BSS 客户端
        params: 查询参数

    Returns:
        Dict: API 响应数据
    """
    request = build_request(params)
    runtime = util_models.RuntimeOptions()

    try:
        resp = client.describe_instance_bill_with_options(request, runtime)
        return resp.body.to_map() if hasattr(resp.body, 'to_map') else resp.body
    except Exception as e:
        raise Exception(f"查询账单失败: {str(e)}")


def query_all_pages(
    client: BssOpenApi20171214Client,
    base_params: DescribeInstanceBillParams,
    max_pages: int = 0
) -> List[Dict[str, Any]]:
    """
    分页查询所有账单数据

    Args:
        client: BSS 客户端
        base_params: 基础查询参数（page_num 会被自动迭代）
        max_pages: 最大查询页数，0表示查询所有页面

    Returns:
        List[Dict]: 所有账单明细记录列表
    """
    all_items = []
    page_num = 1
    total_count = None

    while True:
        # 检查最大页数限制
        if max_pages > 0 and page_num > max_pages:
            print(f"\n已达到最大页数限制 {max_pages}，停止查询")
            break

        # 设置当前页码
        current_params = DescribeInstanceBillParams(**asdict(base_params))
        current_params.page_num = page_num

        print(f"正在查询第 {page_num} 页...", end=' ', flush=True)

        # 执行查询
        response = query_single_page(client, current_params)

        # 检查响应状态
        if not response.get('Success'):
            error_msg = response.get('Message', '未知错误')
            raise Exception(f"API 调用失败: {error_msg}")

        data = response.get('Data', {})

        # 获取总记录数（仅在第一页）
        if total_count is None:
            total_count = data.get('TotalCount', 0)
            print(f"总记录数: {total_count}")

        # 提取账单明细
        items = data.get('Items', {}).get('Item', [])
        if not items:
            print("无更多数据")
            break

        all_items.extend(items)
        print(f"获取 {len(items)} 条记录，累计: {len(all_items)}")

        # 检查是否还有下一页
        page_size = data.get('PageSize', current_params.page_size)
        if len(items) < page_size or len(all_items) >= total_count:
            break

        page_num += 1

    return all_items


def parse_args(args: List[str]) -> Dict[str, Any]:
    """
    解析命令行参数

    Args:
        args: 命令行参数列表

    Returns:
        Dict: 解析后的参数字典
    """
    params = {}
    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith('--'):
            key = arg[2:].replace('-', '_')
            if i + 1 < len(args) and not args[i + 1].startswith('--'):
                value = args[i + 1]
                i += 2
            else:
                value = True
                i += 1

            # 类型转换
            if value == 'true':
                value = True
            elif value == 'false':
                value = False
            elif isinstance(value, str) and value.isdigit():
                value = int(value)

            params[key] = value
        else:
            i += 1

    return params


def main(args: List[str]) -> None:
    """
    主函数：执行账单查询

    Args:
        args: 命令行参数
    """
    # 1. 检查凭据配置
    if not check_credentials():
        sys.exit(1)

    # 2. 解析参数
    parsed_args = parse_args(args)

    # 3. 构建参数对象
    try:
        billing_cycle = parsed_args.get('billing_cycle')
        if not billing_cycle:
            raise ValueError("billing_cycle 是必填参数")

        params = DescribeInstanceBillParams(
            billing_cycle=billing_cycle,
            product_code=parsed_args.get('product_code'),
            product_type=parsed_args.get('product_type'),
            subscription_type=parsed_args.get('subscription_type'),
            is_billing_item=parsed_args.get('is_billing_item'),
            page_size=parsed_args.get('page_size', 100),
            is_hide_zero_charge=parsed_args.get('is_hide_zero_charge'),
            billing_date=parsed_args.get('billing_date'),
            granularity=parsed_args.get('granularity'),
            bill_owner_id=parsed_args.get('bill_owner_id')
        )
    except ValueError as e:
        print(f"参数错误: {e}")
        print_usage()
        sys.exit(1)

    # 4. 创建客户端并执行查询
    try:
        client = create_client()

        max_pages = parsed_args.get('max_pages', 0)

        print(f"\n开始查询账单，账期: {billing_cycle}")
        if params.product_code:
            print(f"产品过滤: {params.product_code}")
        if params.subscription_type:
            print(f"订阅类型: {params.subscription_type}")
        if params.granularity:
            print(f"查询粒度: {params.granularity}")
        print()

        # 执行分页查询
        all_items = query_all_pages(client, params, max_pages)

        # 5. 输出结果
        print(f"\n{'='*50}")
        print(f"查询完成，共获取 {len(all_items)} 条记录")
        print(f"{'='*50}\n")

        # 输出 JSON 格式结果
        result = {
            'billing_cycle': billing_cycle,
            'total_records': len(all_items),
            'items': all_items
        }
        print(json.dumps(result, default=str, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)


def print_usage():
    """打印使用说明"""
    print("""
用法: python main.py --billing-cycle <YYYY-MM> [选项]

必需参数:
  --billing-cycle <YYYY-MM>     账期，格式为 YYYY-MM，仅支持最近18个月

可选参数:
  --product-code <code>         产品代码，例如：rds, ecs, oss
  --product-type <type>         产品类型
  --subscription-type <type>    订阅类型：Subscription(预付费) / PayAsYouGo(后付费)
  --is-billing-item <bool>      是否按计费项维度：true/false，默认 false
  --page-size <num>             每页数量，默认 100，最大 300
  --is-hide-zero-charge <bool>  是否隐藏0费用：true/false
  --billing-date <YYYY-MM-DD>   账单日期，仅当 granularity=DAILY 时必填
  --granularity <type>          查询粒度：MONTHLY(月) / DAILY(日)
  --bill-owner-id <id>          资源归属账号ID
  --max-pages <num>             最大查询页数，默认0表示查询所有

示例:
  # 查询 2024年3月全部账单
  python main.py --billing-cycle 2024-03

  # 查询指定产品的后付费账单
  python main.py --billing-cycle 2024-03 --product-code ecs --subscription-type PayAsYouGo

  # 按天粒度查询特定日期
  python main.py --billing-cycle 2024-03 --granularity DAILY --billing-date 2024-03-01

  # 按计费项维度查询
  python main.py --billing-cycle 2024-03 --is-billing-item true
""")


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print_usage()
        sys.exit(0)
    main(sys.argv[1:])
