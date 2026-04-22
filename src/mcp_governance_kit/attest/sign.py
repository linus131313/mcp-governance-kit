"""Sign and verify :class:`Attestation` documents with sigstore keyless.

Sigstore is an optional dependency (``pip install mcp-governance-kit[sign]``).
When it is not installed, :func:`sign_attestation` raises a clear
``SigstoreUnavailable`` and :func:`verify_attestation` rejects any
attestation whose signature kind is ``sigstore-keyless``.

The unsigned path is supported for local development only; production
verifiers MUST reject unsigned attestations.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass

from mcp_governance_kit.attest.schema import (
    Attestation,
    Signature,
    SignatureKind,
)


class SigstoreUnavailableError(RuntimeError):
    """Raised when the sigstore extra has not been installed."""


# Back-compat alias for naming clarity at call sites that predate the
# N818 rename. New code should use ``SigstoreUnavailableError``.
SigstoreUnavailable = SigstoreUnavailableError


@dataclass(frozen=True)
class VerificationResult:
    """Outcome of :func:`verify_attestation`."""

    valid: bool
    signature_kind: SignatureKind
    issuer: str | None
    reasons: tuple[str, ...] = ()


def _canonical_payload(attestation: Attestation) -> bytes:
    """The canonical signing payload excludes the signature block itself."""
    dumped = json.loads(attestation.model_dump_json())
    dumped.pop("signature", None)
    return json.dumps(dumped, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_attestation(attestation: Attestation, *, identity_token: str | None = None) -> Attestation:
    """Return a new Attestation signed with sigstore keyless.

    Parameters
    ----------
    identity_token:
        If provided, used as an OIDC token (useful from GitHub Actions);
        otherwise sigstore falls back to its interactive OAuth flow.
    """
    try:
        from sigstore.sign import SigningContext
    except ImportError as exc:  # pragma: no cover - exercised indirectly
        raise SigstoreUnavailableError(
            "install with `pip install mcp-governance-kit[sign]` to sign attestations"
        ) from exc

    payload = _canonical_payload(attestation)
    signing_context = SigningContext.production()
    with signing_context.signer(identity_token=identity_token) as signer:
        bundle = signer.sign_artifact(payload)

    return attestation.model_copy(
        update={
            "signature": Signature(
                kind=SignatureKind.SIGSTORE_KEYLESS,
                bundle=base64.b64encode(bundle.to_json().encode("utf-8")).decode("ascii"),
            )
        }
    )


def verify_attestation(
    attestation: Attestation,
    *,
    expected_identity: str | None = None,
    expected_issuer: str | None = None,
    allow_unsigned: bool = False,
) -> VerificationResult:
    """Verify the signature on an attestation.

    Parameters
    ----------
    expected_identity:
        Email / GitHub Actions identity to require on the signing
        certificate.
    expected_issuer:
        OIDC issuer to require (e.g. ``https://token.actions.githubusercontent.com``).
    allow_unsigned:
        If True, unsigned attestations are accepted. Production callers
        MUST leave this ``False`` (the default).
    """
    sig = attestation.signature
    if sig.kind is SignatureKind.UNSIGNED:
        if allow_unsigned:
            return VerificationResult(True, sig.kind, issuer=None, reasons=("unsigned-accepted",))
        return VerificationResult(False, sig.kind, issuer=None, reasons=("unsigned-not-allowed",))

    try:
        from sigstore.models import Bundle
        from sigstore.verify import Verifier, policy
    except ImportError:
        return VerificationResult(
            False,
            sig.kind,
            issuer=None,
            reasons=("sigstore-not-installed",),
        )

    if sig.bundle is None:
        return VerificationResult(False, sig.kind, issuer=None, reasons=("missing-bundle",))

    bundle = Bundle.from_json(base64.b64decode(sig.bundle).decode("utf-8"))
    verifier = Verifier.production()
    policy_check = (
        policy.Identity(identity=expected_identity, issuer=expected_issuer)
        if expected_identity and expected_issuer
        else policy.UnsafeNoOp()
    )
    try:
        verifier.verify_artifact(
            input_=_canonical_payload(attestation),
            bundle=bundle,
            policy=policy_check,
        )
    except Exception as exc:  # pragma: no cover - sigstore raises many subclasses
        return VerificationResult(False, sig.kind, issuer=None, reasons=(str(exc),))

    return VerificationResult(True, sig.kind, issuer=expected_issuer)
