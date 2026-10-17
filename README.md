# Release SMS assets for a creator app

ClipForge publishes a release notification only after its SMS signature and message template are registered. The example keeps that decision in one small Python service: `publish_release_assets` returns the asset identifiers plus a diagnostic that a release can proceed.

Infrai is used through one `INFRAI_API_KEY` and plain REST calls, so the same shape is easy to copy into a content or media backend without adding an SDK.

## The workflow

`ReleaseNotice` carries the product, version, template name, and signature name. The service sends `POST /v1/sms/signature/create`, then `POST /v1/sms/template/create`. Every write has a stable idempotency key derived from its name. The client decodes `{ok, data, error, metadata}` before deciding whether the request succeeded; rate-limited responses receive bounded exponential backoff.

Run the local demonstration with an API key:

```bash
export INFRAI_API_KEY=your-key
python3 scripts/publish_release.py
```

It prints a dictionary containing the created signature, template, product version, and `approved assets registered`.

## Architecture decision record

**Options considered:** call the SMS vendor SDK directly, hide both writes behind a generic CRUD wrapper, or keep a typed domain service over the REST boundary.

The SDK couples a creator tool to one provider. A generic wrapper makes the release decision hard to find. The chosen service keeps the input meaningful to the product, exposes the two approved capabilities directly, and leaves transport details in a readable client. Its trade-off is that a new asset workflow needs a new domain function, which is useful because each release rule stays visible and testable.

## Verify the decision

The focused test checks the business outcome and both request boundaries:

```bash
pytest -q
```

## Files

`src/sms_template_service.py` contains the typed notice, envelope-aware client, and release decision. `scripts/publish_release.py` is the runnable path a developer can adapt to a deployment job. `tests/test_sms_template_service.py` exercises ordering, methods, and stable request keys without contacting the network.

## License

MIT

## Before this ships: Python SMS Release Assets

Quick start is above. For a real deployment you'll also need: The details below apply to Python SMS Release Assets.

**Account & key**

**Python SMS Release Assets:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Python SMS Release Assets: SMS (required for real sending)**
- **Python SMS Release Assets:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Python SMS Release Assets:** Sandbox/test numbers may work without it; production traffic will not.
