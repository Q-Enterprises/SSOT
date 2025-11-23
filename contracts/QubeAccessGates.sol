// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

/// @dev Minimal multisig interface for quorum checks
interface IMultisig {
    function isQuorumMet(bytes32 txHash) external view returns (bool);
}

/// @dev Verifies off-chain SSOT bundles
interface ISSOTVerifier {
    function isValidBundle(bytes calldata bundleData) external view returns (bool);
}

contract QubeAccessGates {
    /* Gate contracts & parameters */
    IERC1155 public immutable councilSBT;     // Gate_GovCommit: Council SBT (Soulbound Token)
    IERC1155 public immutable capBadge;       // Gate_Stake: CAP badge (SBT)
    IERC20 public immutable cptERC20;         // Gate_Trade & Gate_Mint: Capsule Token
    ISSOTVerifier public immutable ssotVerifier;  // Gate_IndexAdmin
    IMultisig public immutable multisig;      // Gate_GovCommit
    address public immutable distributor;     // Gate_Mint
    address public immutable governor;        // Gate_Anchor
    bytes32 public merkleRoot;               // Gate_Claim

    constructor(
        address _councilSBT,
        address _capBadge,
        address _cptERC20,
        address _ssotVerifier,
        address _multisig,
        address _distributor,
        address _governor,
        bytes32 _merkleRoot
    ) {
        councilSBT = IERC1155(_councilSBT);
        capBadge = IERC1155(_capBadge);
        cptERC20 = IERC20(_cptERC20);
        ssotVerifier = ISSOTVerifier(_ssotVerifier);
        multisig = IMultisig(_multisig);
        distributor = _distributor;
        governor = _governor;
        merkleRoot = _merkleRoot;
    }

    /// Gate_GovCommit
    modifier onlyCouncil(bytes32 txHash) {
        require(
            councilSBT.balanceOf(msg.sender, /*SBT_ID*/ 1) > 0,
            "Gate_GovCommit: Insufficient SBT"
        );
        require(multisig.isQuorumMet(txHash), "Gate_GovCommit: Quorum not met");
        _;
    }

    /// Gate_UIAdmin
    modifier onlyUIAdmin() {
        // enforced off-chain via CI/CD tokens & protected branches
        _;
    }

    /// Gate_IndexAdmin
    modifier onlySignedBundle(bytes calldata bundleData) {
        require(ssotVerifier.isValidBundle(bundleData), "Gate_IndexAdmin: Invalid signed bundle");
        _;
    }

    /// Gate_Mint
    modifier onlyDistributor() {
        require(msg.sender == distributor, "Gate_Mint: Unauthorized minter");
        _;
    }

    /// Gate_Anchor
    modifier onlyGovernor() {
        require(msg.sender == governor, "Gate_Anchor: Unauthorized governor");
        _;
    }

    /// Gate_Claim
    function claim(bytes32[] calldata proof, uint256 amount) external {
        // verify Merkle proof for claim eligibility
        bytes32 leaf = keccak256(abi.encodePacked(msg.sender, amount));
        require(MerkleProof.verify(proof, merkleRoot, leaf), "Gate_Claim: Invalid proof");

        // Gate_Stake (CAP badge check) for claimers
        require(capBadge.balanceOf(msg.sender, /*CAP_ID*/ 1) > 0, "Gate_Stake: CAP badge required");

        // transfer CPT tokens
        require(cptERC20.transfer(msg.sender, amount), "Gate_Claim: ERC20 transfer failed");
    }

    /// Gate_Stake
    function stake(uint256 amount) external {
        require(capBadge.balanceOf(msg.sender, /*CAP_ID*/ 1) > 0, "Gate_Stake: CAP badge required");
        require(
            cptERC20.transferFrom(msg.sender, address(this), amount),
            "Gate_Stake: ERC20 transferFrom failed"
        );
    }

    // Example admin functions wired to modifiers

    function mintCPT(address to, uint256 amount) external onlyDistributor {
        // distributor logic to mint CPT
        // e.g. CPTDistributor(distributor).mint(to, amount);
    }

    function anchorEpoch(bytes32 metaHash) external onlyGovernor {
        // anchor metaHash on L1 or in on-chain store
    }

    function registerBundle(bytes calldata bundleData) external onlySignedBundle(bundleData) {
        // write to SSOT or emit event
    }

    function commitPolicy(bytes32 txHash) external onlyCouncil(txHash) {
        // governance commit logic
    }
}
