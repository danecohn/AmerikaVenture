# Vigil Venture release compatibility

This PR follows the **actual published Zen release branch**, rather than replacing it with the unrelated Firefox-only main build. The upstream Zen pin and hashes, app profile Name/Vendor/Profile/RemotingName, org.altstack.venture, paths, filenames, manual update policy and MPL notices remain unchanged. Display names and exact supplied icons are updated. Existing AltStack Search and @altstack remain registered; Vigil Search/@vigil is additive and is the distribution default. No saved engine or user profile is removed.

Six matching-CPU build, browser launch and runtime search/new-tab checks run before publication. PRs cannot publish. New tag -4 is used, and an existing tag cannot be overwritten. Canonical Vigil Sans fonts are copied without alteration. Native contrast/state verification is recorded separately; do not infer exhaustive certification from palette comments.
