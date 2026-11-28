# MFCase Complete updater candidate checkpoint

Status: NATIVE WINDOWS VALIDATION PASSED — HOLD PUBLICATION APPROVAL.

- Original v1.0.3 archive SHA-256: c603da2dc5e9e9d133842158aef701f7382a3ae92e6a500196048f2dea291175.
- Candidate v1.0.4 update archive SHA-256: df7dca49862e6faa7662b47df3f76202db9b4c09a8a2e34cd09209ab1c7783a7 (148083 bytes).
- Candidate full installer SHA-256: a7adfd25694801ed90b7759407295dba83fefd1c768822f3b3cd1b87e9a9e29f.
- User-supplied native Windows report: Windows, Python 3.11.9, PASS, all 12 checks PASS including 31 application regressions, actual v1.0.3 UPDATE button with loopback HTTP, external installation and actual GUI restart, exact installed candidate files, wrong-product/digest/non-newer rejection, rollback, settings/learning and separate standalone MFCase preservation. All three hashes independently matched to local archive bytes and candidate manifest. Linux run also passed.
- The test maps exact GitHub-compatible manifest/asset URLs to loopback. Live GitHub feed, actual trained OCR and full installer execution remain unverified. Cross-drive rollback is not established by this report.
- Public repository staging branch contains only feed metadata. Do not upload application payload or activate main without explicit public publication approval. Expected asset: updates/1.0.4/MFCaseComplete_Update.zip. Preserve main 2be7792e5c8832dfe780dd74e40432695e6b0010, standalone main a1fdeac813949adc7f2f7c1d9707669d1bcbb1e9, settings and learning. Before activation verify exact asset hash, complete feed and privacy boundaries. Activate manifest and asset together, then verify public download and end-to-end production-channel update on disposable copies. No release published.
