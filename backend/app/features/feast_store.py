import pandas as pd
from pathlib import Path
from feast import FeatureStore
from app.config import get_settings
from app.core.logging import LOGGER

_store: FeatureStore | None = None


def get_feast_store() -> FeatureStore | None:
    global _store
    if _store is not None:
        return _store
    try:
        settings = get_settings()
        _store = FeatureStore(repo_path=settings.feast_repo_path)
        LOGGER.info("feast_connected")
    except Exception as e:
        LOGGER.error("feast_connection_failed", error=str(e))
    return _store


def get_online_features(entity_rows: list[dict], features: list[str]) -> dict | None:
    store = get_feast_store()
    if store is None:
        return None
    try:
        result = store.get_online_features(
            features=features, entity_rows=entity_rows
        ).to_dict()
        LOGGER.info("feast_features_retrieved", rows=len(entity_rows))
        return result
    except Exception as e:
        LOGGER.error("feast_feature_retrieval_failed", error=str(e))
        return None


def push_online_features(entity_id: str, feature_data: dict) -> bool:
    store = get_feast_store()
    if store is None:
        return False
    try:
        store.push("fraud_transaction_push_source", features=feature_data)
        LOGGER.info("feast_features_pushed", entity_id=entity_id)
        return True
    except Exception as e:
        LOGGER.error("feast_push_failed", error=str(e))
        return False


def get_feast_info() -> dict:
    store = get_feast_store()
    if store is None:
        return {"connected": False, "error": "Feast store not initialized"}
    try:
        repo_path = Path(get_settings().feast_repo_path)
        fv_list = store.list_feature_views()
        entities = store.list_entities()
        data_sources = store.list_data_sources()
        result = {
            "connected": True,
            "online_store": "redis",
            "offline_store": "file",
            "feature_views": [],
            "entities": [],
            "push_sources": [],
        }
        for ent in entities:
            result["entities"].append({
                "name": ent.name,
                "join_keys": list(ent.join_keys) if hasattr(ent, "join_keys") else [],
            })
        for fv in fv_list:
            fields = []
            for f in fv.schema:
                fields.append({"name": f.name, "dtype": str(f.dtype).split(".")[-1]})
            fv_info = {
                "name": fv.name,
                "ttl": str(fv.ttl) if fv.ttl else "N/A",
                "fields": fields,
                "entities": [e for e in fv.entities],
            }
            parquet_path = repo_path / "data" / f"{fv.name.replace('stats', 'features')}.parquet"
            if parquet_path.exists():
                try:
                    df = pd.read_parquet(parquet_path)
                    stats = {}
                    for col in df.select_dtypes(include=["number"]).columns:
                        stats[col] = {
                            "count": int(df[col].count()),
                            "min": float(df[col].min()) if pd.notna(df[col].min()) else None,
                            "max": float(df[col].max()) if pd.notna(df[col].max()) else None,
                            "mean": float(df[col].mean()) if pd.notna(df[col].mean()) else None,
                            "nulls": int(df[col].isna().sum()),
                        }
                    non_num = df.select_dtypes(exclude=["number"]).columns.tolist()
                    fv_info["row_count"] = len(df)
                    fv_info["stats"] = stats
                    fv_info["non_numeric_cols"] = non_num
                except Exception as e:
                    fv_info["stats_error"] = str(e)
            result["feature_views"].append(fv_info)
        for ds in data_sources:
            if hasattr(ds, "name") and ds.name:
                result["push_sources"].append({"name": ds.name})
        LOGGER.info("feast_info_retrieved", views=len(result["feature_views"]))
        return result
    except Exception as e:
        LOGGER.error("feast_info_failed", error=str(e))
        return {"connected": False, "error": str(e)}
