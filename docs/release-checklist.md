# Release checklist (maintainers only)

## One-time PyPI setup (required before the first release)

1. Create a PyPI account at <https://pypi.org/account/register/>.
2. Enable 2FA.
3. Go to <https://pypi.org/manage/account/publishing/> and add a
   **pending publisher** for the project that does not yet exist on
   PyPI:
   - PyPI project name: `mcp-governance-kit`
   - Owner: `linus131313`
   - Repository name: `mcp-governance-kit`
   - Workflow name: `release.yml`
   - Environment name: `pypi`
4. On GitHub, open
   <https://github.com/linus131313/mcp-governance-kit/settings/environments>
   and create an environment named `pypi` (required branches can be
   set to `main` for extra safety).

After step 3, the first successful `release.yml` run will create the
project on PyPI under the pending publisher. No API tokens are needed.

## Per-release steps

1. Decide the version number and update `CHANGELOG.md`'s `[Unreleased]`
   section; rename it to the new version with today's date.
2. Commit the changelog: `git commit -m "Release v0.x.y"`.
3. Tag: `git tag -s v0.x.y -m "v0.x.y"` (or unsigned `git tag v0.x.y`
   if you do not sign tags).
4. Push: `git push origin main v0.x.y`.
5. Watch <https://github.com/linus131313/mcp-governance-kit/actions>
   for the `release.yml` run. It will:
   - build sdist + wheel via `hatch`,
   - upload them to PyPI via trusted publishing (OIDC, no token),
   - sign them with sigstore keyless,
   - create a GitHub Release with the signed artefacts.
6. Verify: `pip install --upgrade mcp-governance-kit` on a clean venv
   picks up the new version.

## Post-release smoke tests

```bash
pip install 'mcp-governance-kit[sign]' --upgrade
mcp-gov version
mcp-gov tcs reference
mcp-gov attest examples/c3-developer.mcp.json --host-id smoke --out /tmp/smoke.json
mcp-gov check /tmp/smoke.json --policy policies/default.yaml
```

All four commands should succeed.
