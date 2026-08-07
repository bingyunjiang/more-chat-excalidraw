# 技术组件预定义样式模板

> 50+ 常见技术组件预定义样式，架构图生成时自动根据技术名称匹配对应形状/颜色/图标占位。
> 参考：BV-Venky/excalidraw-architect-mcp（139★）

## 匹配规则

生成架构图时，按以下优先级匹配技术组件样式：
1. 精确匹配：技术名称（如 "PostgreSQL"）完全匹配
2. 模糊匹配：技术名称包含关键词（如 "Kafka"、"Redis"）
3. 归类匹配：按类型（如 "数据库"、"消息队列"）匹配默认样式
4. 兜底：通用矩形样式

## 1. 数据库

| 技术 | 形状 | 填充色 | 文字色 | 特殊标记 |
|------|------|--------|--------|----------|
| PostgreSQL | 椭圆 | `#c3fae8` 浅青 | `#1e4a3a` | 无 |
| MySQL | 椭圆 | `#c3fae8` 浅青 | `#1e4a3a` | 无 |
| MariaDB | 椭圆 | `#c3fae8` 浅青 | `#1e4a3a` | 无 |
| Oracle | 椭圆 | `#c3fae8` 浅青 | `#1e4a3a` | 无 |
| SQL Server | 椭圆 | `#c3fae8` 浅青 | `#1e4a3a` | 无 |
| MongoDB | 椭圆 | `#b2f2bb` 浅绿 | `#1e3a3a` | 无 |
| Redis | 椭圆 | `#fcc2d7` 浅粉 | `#5f1e3a` | 无 |
| Elasticsearch | 矩形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |
| InfluxDB | 矩形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |
| SQLite | 矩形 | `#c3fae8` 浅青 | `#1e4a3a` | 尺寸偏小 140×50 |
| DynamoDB | 椭圆 | `#c3fae8` 浅青 | `#1e4a3a` | 无 |
| Spanner | 椭圆 | `#c3fae8` 浅青 | `#1e4a3a` | 无 |
| HBase | 矩形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |
| TiDB | 椭圆 | `#c3fae8` 浅青 | `#1e4a3a` | 无 |
| ClickHouse | 矩形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |
| Neo4j | 椭圆 | `#c3fae8` 浅青 | `#1e4a3a` | 无 |
| Cassandra | 椭圆 | `#c3fae8` 浅青 | `#1e4a3a` | 无 |

**默认数据库样式**（未匹配到具体技术时）：
```json
{
  "type": "ellipse",
  "width": 120, "height": 60,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#c3fae8",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 1
}
```

## 2. 消息队列 / 流处理

| 技术 | 形状 | 填充色 | 文字色 | 特殊标记 |
|------|------|--------|--------|----------|
| Kafka | 矩形 | `#ffd8a8` 浅橙 | `#5f3a1e` | 无 |
| RabbitMQ | 矩形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |
| SQS | 矩形 | `#fff3bf` 浅黄 | `#5f4a1e` | 无 |
| SNS | 矩形 | `#fff3bf` 浅黄 | `#5f4a1e` | 无 |
| Pulsar | 矩形 | `#ffd8a8` 浅橙 | `#5f3a1e` | 无 |
| ActiveMQ | 矩形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |
| RocketMQ | 矩形 | `#ffd8a8` 浅橙 | `#5f3a1e` | 无 |
| NATS | 矩形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |
| ZeroMQ | 矩形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |
| Flink | 矩形 | `#ffd8a8` 浅橙 | `#5f3a1e` | 圆角 |
| Spark Streaming | 矩形 | `#ffd8a8` 浅橙 | `#5f3a1e` | 圆角 |
| Kinesis | 矩形 | `#fff3bf` 浅黄 | `#5f4a1e` | 无 |
| Pub/Sub | 矩形 | `#fff3bf` 浅黄 | `#5f4a1e` | 无 |

**默认消息队列样式**：
```json
{
  "type": "rectangle",
  "width": 180, "height": 60,
  "roundness": { "type": 3 },
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#ffd8a8",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 1
}
```

## 3. 存储 / 对象存储

| 技术 | 形状 | 填充色 | 文字色 | 特殊标记 |
|------|------|--------|--------|----------|
| S3 | 圆角矩形 | `#c3fae8` 浅青 | `#1e4a3a` | 圆角 |
| GCS | 圆角矩形 | `#c3fae8` 浅青 | `#1e4a3a` | 圆角 |
| Blob Storage | 圆角矩形 | `#c3fae8` 浅青 | `#1e4a3a` | 圆角 |
| MinIO | 圆角矩形 | `#c3fae8` 浅青 | `#1e4a3a` | 圆角 |
| HDFS | 矩形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |
| Ceph | 圆角矩形 | `#c3fae8` 浅青 | `#1e4a3a` | 圆角 |
| EBS | 矩形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |
| EFS | 矩形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |
| NFS | 矩形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |

**默认存储样式**：
```json
{
  "type": "rectangle",
  "width": 160, "height": 60,
  "roundness": { "type": 3 },
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#c3fae8",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 1
}
```

## 4. 网关 / 负载均衡

| 技术 | 形状 | 填充色 | 文字色 | 特殊标记 |
|------|------|--------|--------|----------|
| Nginx | 菱形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |
| API Gateway | 菱形 | `#fff3bf` 浅黄 | `#5f4a1e` | 无 |
| Kong | 菱形 | `#ffd8a8` 浅橙 | `#5f3a1e` | 无 |
| Traefik | 菱形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |
| Envoy | 菱形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |
| HAProxy | 菱形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |
| ALB | 菱形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |
| CloudFront | 菱形 | `#fff3bf` 浅黄 | `#5f4a1e` | 无 |

**默认网关样式**：
```json
{
  "type": "diamond",
  "width": 140, "height": 70,
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#a5d8ff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 1
}
```

## 5. 计算 / 运行时

| 技术 | 形状 | 填充色 | 文字色 | 特殊标记 |
|------|------|--------|--------|----------|
| Lambda | 圆角矩形 | `#b2f2bb` 浅绿 | `#1e3a3a` | 圆角 |
| EC2 | 矩形 | `#ffffff` 白色 | `#374151` | 无 |
| Fargate | 圆角矩形 | `#b2f2bb` 浅绿 | `#1e3a3a` | 圆角 |
| K8s Pod | 矩形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |
| Docker | 矩形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |
| VM | 矩形 | `#ffffff` 白色 | `#374151` | 无 |
| Bare Metal | 矩形 | `#ffffff` 白色 | `#374151` | 无 |

**默认计算样式**：
```json
{
  "type": "rectangle",
  "width": 160, "height": 60,
  "roundness": { "type": 3 },
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#ffffff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 1
}
```

## 6. 缓存 / CDN

| 技术 | 形状 | 填充色 | 文字色 | 特殊标记 |
|------|------|--------|--------|----------|
| CDN | 圆角矩形 | `#fcc2d7` 浅粉 | `#5f1e3a` | 圆角 |
| CloudFront | 圆角矩形 | `#fcc2d7` 浅粉 | `#5f1e3a` | 圆角 |
| Memcached | 椭圆 | `#ffd8a8` 浅橙 | `#5f3a1e` | 无 |
| Redis Cache | 椭圆 | `#ffd8a8` 浅橙 | `#5f3a1e` | 无 |
| Varnish | 圆角矩形 | `#fcc2d7` 浅粉 | `#5f1e3a` | 圆角 |

**默认缓存样式**：
```json
{
  "type": "rectangle",
  "width": 140, "height": 60,
  "roundness": { "type": 3 },
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#fcc2d7",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 1
}
```

## 7. 监测 / 可观测性

| 技术 | 形状 | 填充色 | 文字色 | 特殊标记 |
|------|------|--------|--------|----------|
| Prometheus | 矩形 | `#fcc2d7` 浅粉 | `#5f1e3a` | 无 |
| Grafana | 矩形 | `#fcc2d7` 浅粉 | `#5f1e3a` | 无 |
| Datadog | 矩形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |
| New Relic | 矩形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |
| CloudWatch | 矩形 | `#fff3bf` 浅黄 | `#5f4a1e` | 无 |
| Jaeger | 矩形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |
| ELK Stack | 矩形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |

## 8. CI/CD / 自动化

| 技术 | 形状 | 填充色 | 文字色 | 特殊标记 |
|------|------|--------|--------|----------|
| Jenkins | 矩形 | `#ffd8a8` 浅橙 | `#5f3a1e` | 无 |
| GitHub Actions | 矩形 | `#ffffff` 白色 | `#374151` | 无 |
| GitLab CI | 矩形 | `#ffd8a8` 浅橙 | `#5f3a1e` | 无 |
| ArgoCD | 矩形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |
| Terraform | 矩形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |
| Pulumi | 矩形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |
| Ansible | 矩形 | `#ffd8a8` 浅橙 | `#5f3a1e` | 无 |

## 9. 基础设施 / 容器编排

| 技术 | 形状 | 填充色 | 文字色 | 特殊标记 |
|------|------|--------|--------|----------|
| K8s | 矩形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |
| Docker | 矩形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |
| Nomad | 矩形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |
| Consul | 矩形 | `#d0bfff` 浅紫 | `#2e1e5f` | 无 |
| Vault | 矩形 | `#ffc9c9` 浅红 | `#5f1e1e` | 无 |
| Istio | 菱形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |
| Linkerd | 菱形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |
| CoreDNS | 菱形 | `#a5d8ff` 浅蓝 | `#1e3a5f` | 无 |

## 10. 自动匹配 Python 参考

```python
# 技术名称 → 样式匹配逻辑（伪代码参考）
TECH_STYLES = {
    # 按类型分组
    "database": {
        "default": {"type": "ellipse", "bg": "#c3fae8", "fg": "#1e4a3a"},
        "exact": {
            "MongoDB": {"bg": "#b2f2bb"},
            "Redis": {"bg": "#fcc2d7", "fg": "#5f1e3a"},
        }
    },
    "queue": {
        "default": {"type": "rectangle", "bg": "#ffd8a8", "fg": "#5f3a1e"},
        "exact": {
            "RabbitMQ": {"bg": "#d0bfff", "fg": "#2e1e5f"},
        }
    },
    # ... 更多类型
}

def match_tech_style(tech_name: str) -> dict:
    \"\"\"返回 {type, width, height, backgroundColor, strokeColor, roundness, ...}\"\"\"
    name_lower = tech_name.lower()
    # 先尝试精确匹配
    for category, styles in TECH_STYLES.items():
        if tech_name in styles.get("exact", {}):
            base = dict(styles["default"])
            base.update(styles["exact"][tech_name])
            return base
    # 模糊匹配
    if any(kw in name_lower for kw in ["db", "sql", "database"]):
        return TECH_STYLES["database"]["default"]
    if any(kw in name_lower for kw in ["queue", "mq", "stream", "kafka"]):
        return TECH_STYLES["queue"]["default"]
    # 兜底
    return {"type": "rectangle", "width": 160, "height": 60, "backgroundColor": "#ffffff"}
```
