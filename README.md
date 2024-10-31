<!-- SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in> -->
<!-- SPDX-License-Identifier: CC0-1.0 -->

how-much-work
=============

[![Build Status](https://drone.tildegit.org/api/badges/CyberTaIlor/how-much-work/status.svg)](https://drone.tildegit.org/CyberTaIlor/how-much-work)

how-much-work is a utility for distro maintainers that helps them estimate the
amount of work needed to package a project.


Installing
----------

### Gentoo

```sh
eselect repository enable guru
emaint sync -r guru
emerge dev-util/how-much-work
```

### Other systems

`pip install how-much-work --user`


Packaging
---------

You can track new releases using an [atom feed][atom] provided by PyPI.

[atom]: https://pypi.org/rss/project/how-much-work/releases.xml


Contributing
------------

Patches and pull requests are welcome. Please use either [git-send-email(1)][1]
or [git-request-pull(1)][2], addressed to <cyber@sysrq.in>.

If you prefer GitHub-style workflow, use the [mirror repo][gh] to send pull
requests.

Your commit message should conform to the following standard:

```
file/changed: Concice and complete statement of the purpose

This is the body of the commit message.  The line above is the
summary.  The summary should be no more than 72 chars long.  The
body can be more freely formatted, but make it look nice.  Make
sure to reference any bug reports and other contributors.  Make
sure the correct authorship appears.
```

[1]: https://git-send-email.io/
[2]: https://git-scm.com/docs/git-request-pull
[gh]: http://github.com/cybertailor/how-much-work


IRC
---

You can join the `#how-much-work` channel either on [Libera Chat][libera] or
[via Matrix][matrix].

[libera]: https://libera.chat/
[matrix]: https://matrix.to/#/#how-much-work:sysrq.in


License
-------

WTFPL
