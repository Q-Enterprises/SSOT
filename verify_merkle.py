import hashlib
from ssot.ledger_emitter import merkle_root_from_leaves, _leaf_hash, _node_hash, _empty_root, sha256_digest

def test_merkle():
    # Test empty
    root = merkle_root_from_leaves([])
    print(f"Empty root: {root}")
    assert root == _empty_root()

    # Test single leaf
    leaf1 = sha256_digest(b"leaf1")
    root = merkle_root_from_leaves([leaf1])
    print(f"Single leaf root: {root}")
    expected_leaf_hash = _leaf_hash(leaf1)
    # With 1 leaf, the root is sha256:hex(leaf_hash) ??
    # Wait, looking at the code:
    # nodes = [_leaf_hash(leaf) for leaf in leaves]
    # while len(nodes) > 1: ...
    # return "sha256:" + nodes[0].hex()

    # So if 1 leaf, loop doesn't run, returns leaf hash directly.
    assert root == "sha256:" + expected_leaf_hash.hex()

    # Test two leaves
    leaf2 = sha256_digest(b"leaf2")
    root = merkle_root_from_leaves([leaf1, leaf2])
    print(f"Two leaves root: {root}")

    h1 = _leaf_hash(leaf1)
    h2 = _leaf_hash(leaf2)
    h_root = _node_hash(h1, h2)
    assert root == "sha256:" + h_root.hex()

    # Test three leaves (1, 2, 3) -> (1,2), (3,3) -> ((1,2), (3,3))
    leaf3 = sha256_digest(b"leaf3")
    root = merkle_root_from_leaves([leaf1, leaf2, leaf3])
    print(f"Three leaves root: {root}")

    h3 = _leaf_hash(leaf3)
    h12 = _node_hash(h1, h2)
    h33 = _node_hash(h3, h3)
    h_root_3 = _node_hash(h12, h33)
    assert root == "sha256:" + h_root_3.hex()

    print("Verification successful!")

if __name__ == "__main__":
    test_merkle()
