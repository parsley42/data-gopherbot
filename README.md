# Mr. Data

`Data` is the **Gopherbot** robot that runs in my home Kubernetes cluster, and is responsible for building and publishing `gopherbot` containers, documentation, etc.

Besides the usual config for **Gopherbot** robots, there are some other files of interest:
* `Containerfile` - for building the custom container for Data, which includes e.g. `mdbook` and `buildah`
* `containers.conf` - required by the containerfile
* `build.sh`, `push.sh`, `tagpush.sh` - scripts I use that probably aren't of value to anybody else
