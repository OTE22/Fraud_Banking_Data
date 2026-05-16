from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, PushSource
from feast.types import Float32, Int32, Int64, Bool

customer = Entity(name="customer_id", join_keys=["customer_id"])
merchant = Entity(name="merchant_id", join_keys=["merchant_id"])
transaction = Entity(name="transaction_id", join_keys=["transaction_id"])

customer_source = FileSource(
    path="data/customer_features.parquet",
    timestamp_field="event_timestamp",
)

merchant_source = FileSource(
    path="data/merchant_features.parquet",
    timestamp_field="event_timestamp",
)

customer_profile_source = FileSource(
    path="data/customer_profile_features.parquet",
    timestamp_field="event_timestamp",
)

anomaly_feature_source = FileSource(
    path="data/anomaly_features.parquet",
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

customer_profiles = FeatureView(
    name="customer_profiles",
    entities=[customer],
    ttl=timedelta(days=90),
    schema=[
        Field(name="age", dtype=Int32),
        Field(name="annual_income", dtype=Float32),
        Field(name="credit_score", dtype=Int32),
        Field(name="account_balance", dtype=Float32),
        Field(name="tenure_months", dtype=Int32),
        Field(name="transaction_frequency_30d", dtype=Int32),
        Field(name="avg_transaction_amount", dtype=Float32),
        Field(name="num_fraudulent_tx_90d", dtype=Int32),
        Field(name="high_risk_flag", dtype=Int32),
        Field(name="segment_label", dtype=Int32),
    ],
    source=customer_profile_source,
)

anomaly_features = FeatureView(
    name="anomaly_features",
    entities=[transaction],
    ttl=timedelta(days=7),
    schema=[
        Field(name="amount", dtype=Float32),
        Field(name="log_amount", dtype=Float32),
        Field(name="balance_diff_orig", dtype=Float32),
        Field(name="balance_diff_dest", dtype=Float32),
        Field(name="amt_to_balance_ratio", dtype=Float32),
        Field(name="oldbalanceOrg", dtype=Float32),
        Field(name="newbalanceOrig", dtype=Float32),
        Field(name="oldbalanceDest", dtype=Float32),
        Field(name="newbalanceDest", dtype=Float32),
        Field(name="anomaly_score", dtype=Float32),
    ],
    source=anomaly_feature_source,
)
