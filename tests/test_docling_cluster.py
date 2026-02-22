import pytest
import uuid
from docling_cluster import DriftReceipt, DocBlock, build_doc_blocks_from_drift

def test_build_doc_blocks_happy_path():
    # Arrange
    sample_ids = [f"id_{i}" for i in range(100)]
    receipt = DriftReceipt(
        drift_id="drift_123",
        store="main_store",
        collection="docs",
        drift_class="outlier",
        sample_size=100,
        counts={"total": 100},
        qdrant_ref={"sample_ids": sample_ids}
    )

    # Act
    blocks = build_doc_blocks_from_drift(receipt, block_size=32)

    # Assert
    # 100 / 32 = 3.125 -> 4 blocks
    assert len(blocks) == 4
    assert blocks[0].doc_ids == sample_ids[0:32]
    assert blocks[1].doc_ids == sample_ids[32:64]
    assert blocks[2].doc_ids == sample_ids[64:96]
    assert blocks[3].doc_ids == sample_ids[96:100]

    for block in blocks:
        assert isinstance(block, DocBlock)
        assert block.drift_class == "outlier"
        assert block.collection == "docs"
        assert isinstance(uuid.UUID(block.block_id), uuid.UUID)

def test_build_doc_blocks_custom_size():
    # Arrange
    sample_ids = [f"id_{i}" for i in range(10)]
    receipt = DriftReceipt(
        drift_id="drift_123",
        store="main_store",
        collection="docs",
        drift_class="outlier",
        sample_size=10,
        counts={"total": 10},
        qdrant_ref={"sample_ids": sample_ids}
    )

    # Act
    blocks = build_doc_blocks_from_drift(receipt, block_size=5)

    # Assert
    assert len(blocks) == 2
    assert blocks[0].doc_ids == sample_ids[0:5]
    assert blocks[1].doc_ids == sample_ids[5:10]

def test_build_doc_blocks_partial_last():
    # Arrange
    sample_ids = [f"id_{i}" for i in range(7)]
    receipt = DriftReceipt(
        drift_id="drift_123",
        store="main_store",
        collection="docs",
        drift_class="outlier",
        sample_size=7,
        counts={"total": 7},
        qdrant_ref={"sample_ids": sample_ids}
    )

    # Act
    blocks = build_doc_blocks_from_drift(receipt, block_size=3)

    # Assert
    assert len(blocks) == 3
    assert len(blocks[0].doc_ids) == 3
    assert len(blocks[1].doc_ids) == 3
    assert len(blocks[2].doc_ids) == 1
    assert blocks[2].doc_ids == ["id_6"]

def test_build_doc_blocks_empty_ids():
    # Arrange
    receipt = DriftReceipt(
        drift_id="drift_123",
        store="main_store",
        collection="docs",
        drift_class="outlier",
        sample_size=0,
        counts={"total": 0},
        qdrant_ref={"sample_ids": []}
    )

    # Act
    blocks = build_doc_blocks_from_drift(receipt)

    # Assert
    assert len(blocks) == 0

def test_build_doc_blocks_missing_ids_key():
    # Arrange
    receipt = DriftReceipt(
        drift_id="drift_123",
        store="main_store",
        collection="docs",
        drift_class="outlier",
        sample_size=0,
        counts={"total": 0},
        qdrant_ref={} # Missing sample_ids
    )

    # Act
    blocks = build_doc_blocks_from_drift(receipt)

    # Assert
    assert len(blocks) == 0

def test_build_doc_blocks_metadata():
    # Arrange
    receipt = DriftReceipt(
        drift_id="drift_456",
        store="other_store",
        collection="other_collection",
        drift_class="concept_drift",
        sample_size=1,
        counts={"total": 1},
        qdrant_ref={"sample_ids": ["id_1"]}
    )

    # Act
    blocks = build_doc_blocks_from_drift(receipt)

    # Assert
    assert len(blocks) == 1
    assert blocks[0].drift_class == "concept_drift"
    assert blocks[0].collection == "other_collection"
    assert blocks[0].created_at_utc > 0
