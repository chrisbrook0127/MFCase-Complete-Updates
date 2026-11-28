# MFCase Complete updater candidate checkpoint

Status: HOLD — private native Windows validation and publication approval required.

- Approved baseline: exact v1.0.3 full installer SHA-256 c603da2dc5e9e9d133842158aef701f7382a3ae92e6a500196048f2dea291175.
- Numeric v1.0.4 test candidate required by existing updater parser; not a stable release.
- Candidate update archive SHA-256 df7dca49862e6faa7662b47df3f76202db9b4c09a8a2e34cd09209ab1c7783a7 (148083 bytes). Candidate full installer SHA-256 a7adfd25694801ed90b7759407295dba83fefd1c768822f3b3cd1b87e9a9e29f.
- Local Linux 31/31 inherited regressions passed. Isolated actual v1.0.3 GUI UPDATE button -> exact loopback HTTP feed -> external updater -> real v1.0.4 GUI restart passed; synthetic learning/settings and separate MFCase data unchanged. Candidate helper rollback, digest, wrong-product and non-newer rejection passed. No actual models, production data or real GitHub download tested.
- Private Windows validation bundle created. Require actual Windows PASS report with exact baseline and candidate hashes and all twelve check fields PASS. Test routes only exact manifest and asset paths to loopback, suppresses only desktop shortcut creation in disposable copy, uses original VBS launcher. Full installer execution and real trained OCR remain separate gates.
- On this public staging branch the zero-byte updates placeholder is replaced with the feed folder and actual candidate manifest, but no application payload. Do not open a merge or activate feed without verified Windows result and explicit authorization to publish public payload. main and all sibling applications stay unchanged. Before eventual activation verify actual payload digest, complete staged feed, no existing release collision, privacy and explicit approval; publish manifest and payload in same guarded commit. Verify live download and installed version after publication.
