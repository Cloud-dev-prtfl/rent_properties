# ADR-0012: SeaweedFS as the local S3 emulator

Decides which S3-compatible service the docker compose stack uses, so that listing-photo uploads (presigned POST, M2) work offline without AWS credentials.

Status: Draft v0.1 (2026-10-27)

| | |
|---|---|
| Decision status | Accepted (M0) |
| Date | 2026-10-27 |
| Deciders | Tech Lead |
| Consulted | Platform |
| Supersedes / superseded by | — |
| Requirements | NFR-MAINT-01 (one-command local environment, US-003) |
| Gap / open question | Register R-58; infrastructure INF-D2 |
| Related | [ADR-0009 direct-to-S3 upload](0009-s3-direct-upload-async-image-processing.md), [Infrastructure §3.3](../architecture/04-infrastructure-and-deployment.md) |

## Context and problem statement

The baseline named MinIO or LocalStack. The MinIO community edition moved to source-only distribution (no maintained images), and LocalStack's S3 emulation brings a much heavier container. We need presigned POST with policy conditions (content-length range, content-type), which is what the upload pipeline in M2 relies on.

## Decision drivers

- Multi-arch image (Apple Silicon and x86 CI).
- Supports presigned POST policies and the S3 API calls `django-storages`/boto3 make.
- Small, fast to start, Apache-2.0 licensed.

## Considered options

1. **SeaweedFS** (`chrislusf/seaweedfs`, `server -s3`).
2. LocalStack (S3 only).
3. MinIO (community, built from source).

## Decision outcome

**Option 1, SeaweedFS 3.97**, pinned in `compose.yaml`, with static identities in `docker/seaweedfs/s3.json` (local-only keys). If the M2 presigned-POST check finds a gap, fall back to LocalStack S3 with no code changes, because the endpoint URL is configuration.

### Consequences

- **Positive:** a lightweight, multi-arch emulator in the default stack; developers need no AWS account.
- **Negative:** not byte-identical with S3 semantics. Contract tests against real S3 run on `dev` (nightly).
- **Neutral / follow-on:** local CORS settings for the presigned POST are configured in M2.

### Confirmation

The `s3` service starts in compose (M0). M2 adds an integration test that performs a presigned POST against it.

## Deviations from the SRS

None (local tooling only).
