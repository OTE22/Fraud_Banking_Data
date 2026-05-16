from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, PushSource
from feast.types import Float32, Int32, Bool

customer = Entity(name="customer_id", join_keys=["customer_id"])
merchant = Entity(name="merchant_id", join_keys=["merchant_id"])

customer_source = FileSource(
    path="data/customer_features.parquet",
    timestamp_field="event_timestamp",
)

merchant_source = FileSource(
    path="data/merchant_features.parquet",
    timestamp_field="event_timestamp",
)

push_source = PushSource(
    name="fraud_transaction_push_source",
    batch_source=FileSource(
        path="data/transaction_push.parquet",
        timestamp_field="event_timestamp",
    ),
)

customer_stats = FeatureView(
    name="customer_stats",
    entities=[customer],
    ttl=timedelta(days=30),
    schema=[
        Field(name="avg_transaction_amount_30d", dtype=Float32),
        Field(name="transaction_count_30d", dtype=Int32),
        Field(name="is_high_risk_merchant_30d", dtype=Bool),
    ],
    source=customer_source,
)

merchant_stats = FeatureView(
    name="merchant_stats",
    entities=[merchant],
    ttl=timedelta(days=7),
    schema=[
        Field(name="avg_merchant_amount", dtype=Float32),
        Field(name="merchant_fraud_rate_7d", dtype=Float32),
    ],
    source=merchant_source,
)
