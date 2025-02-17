// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GenomicDataDID {
    
    struct GenomicRecord {
        string dataHash;  // SHA-256 hash of genomic data
        string ipfsLink;  // Encrypted genomic data stored on IPFS
        string ownerDID;  // DID of the data owner (patient)
        mapping(string => bool) accessList;  // Access control using DIDs
    }

    mapping(uint256 => GenomicRecord) public genomicRecords;
    uint256 public recordCount = 0;

    event DataStored(uint256 indexed recordId, string dataHash, string ipfsLink, string ownerDID);
    event AccessGranted(uint256 indexed recordId, string indexed researcherDID);
    event AccessRevoked(uint256 indexed recordId, string indexed researcherDID);

    /**
     * @dev Store genomic data on blockchain with DID-based ownership
     * @param _dataHash SHA-256 hash of the genomic data for integrity verification
     * @param _ipfsLink IPFS CID where the encrypted genomic data is stored
     * @param _ownerDID Decentralized Identifier (DID) of the data owner (patient)
     */
    function storeGenomicData(string memory _dataHash, string memory _ipfsLink, string memory _ownerDID) public {
        recordCount++;
        GenomicRecord storage record = genomicRecords[recordCount];
        record.dataHash = _dataHash;
        record.ipfsLink = _ipfsLink;
        record.ownerDID = _ownerDID;

        emit DataStored(recordCount, _dataHash, _ipfsLink, _ownerDID);
    }

    /**
     * @dev Grant access to genomic data based on DID authentication
     * @param _recordId ID of the genomic record
     * @param _researcherDID DID of the researcher requesting access
     */
    function grantAccess(uint256 _recordId, string memory _researcherDID) public {
        require(
            keccak256(abi.encodePacked(genomicRecords[_recordId].ownerDID)) == keccak256(abi.encodePacked(msg.sender)),
            "Not authorized to grant access"
        );
        genomicRecords[_recordId].accessList[_researcherDID] = true;
        emit AccessGranted(_recordId, _researcherDID);
    }

    /**
     * @dev Revoke access to genomic data based on DID authentication
     * @param _recordId ID of the genomic record
     * @param _researcherDID DID of the researcher whose access is revoked
     */
    function revokeAccess(uint256 _recordId, string memory _researcherDID) public {
        require(
            keccak256(abi.encodePacked(genomicRecords[_recordId].ownerDID)) == keccak256(abi.encodePacked(msg.sender)),
            "Not authorized to revoke access"
        );
        genomicRecords[_recordId].accessList[_researcherDID] = false;
        emit AccessRevoked(_recordId, _researcherDID);
    }

    /**
     * @dev Verify if genomic data has been altered using SHA-256 hash
     * @param _recordId ID of the genomic record
     * @param _dataHash The SHA-256 hash of the data to be verified
     * @return bool indicating whether the data is authentic
     */
    function verifyData(uint256 _recordId, string memory _dataHash) public view returns (bool) {
        return keccak256(abi.encodePacked(genomicRecords[_recordId].dataHash)) == keccak256(abi.encodePacked(_dataHash));
    }

    /**
     * @dev Check if a researcher has access to a genomic record
     * @param _recordId ID of the genomic record
     * @param _researcherDID DID of the researcher
     * @return bool indicating whether access is granted
     */
    function checkAccess(uint256 _recordId, string memory _researcherDID) public view returns (bool) {
        return genomicRecords[_recordId].accessList[_researcherDID];
    }
}
