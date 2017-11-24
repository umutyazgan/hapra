# User Manual

This manual explains how the URL's are structured. For more information about
each command, please check
[HAProxy Management Guide](https://cbonte.github.io/haproxy-dconv/1.7/management.html#9.3).
Commands in this manual link to relevant entries in HAProxy Management Guide.

Use `%23` in URL's to escape the `#` characters at the beggining of the `#<id>`
arguments.

## Read-Only Commands

### [`get map <map> <value>`](https://cbonte.github.io/haproxy-dconv/1.7/management.html#9.3-get%20map)

#### URL Structure

```
.../hapra/get/map?map=<id-or-file>&value=<value>
```

* `map`: `#<id>` or the `<file>` returned by `show map`. (**NOTE:** Using
		 `#<id>` for `map` might not work as intended, use `<file>` path
		 instead.)
* `value`: value to look up.

#### Output Format

**Socket Output:**

```sh
type=beg, case=sensitive, found=yes, idx=tree, key="1", value="deneme1", type="str"

```

**Successful API Call Output:**

```JSON
{
	"status": "success",
	"code": "200",
	"response": {
		"type": "value 1",
		"case": "value 2",
		"found": "value 3",
		"idx": "value 4",
		"key": "value 5",
		"value": "value 6",
		"type": "value 7"
	}
}
```
### [`get acl <acl> <value>`](https://cbonte.github.io/haproxy-dconv/1.7/management.html#9.3-get%20acl)

#### URL Structure

```
.../hapra/get/acl?acl=<id-or-file>&value=<value>
```

* `acl`: `#<id>` or the `<file>` returned by `show acl`.
* `value`: value to look up.

### [`get weight <backend>/<server>`](https://cbonte.github.io/haproxy-dconv/1.7/management.html#9.3-get%20weight)

#### URL Structure

```
.../hapra/get/weight?backend=<backend>&server=<server>
```

* `backend`: name of the backend that contains the server
* `server`: name of the server that you want to get weight from

### [`help`](https://cbonte.github.io/haproxy-dconv/1.7/management.html#9.3-help)

#### URL Structure

```
.../hapra/help
```

### [`show env [<name>]`](https://cbonte.github.io/haproxy-dconv/1.7/management.html#9.3-show%20env)

#### URL Structure

```
.../hapra/show/env?name=<name>
```

* `name`: name of the variable you want to show

#### Output Format

**Socket Output:**

```sh
ENV_VAR_1=VALUE_1
ENV_VAR_2=VALUE_2
ENV_VAR_3=VALUE_3
```

**Successful API Call Output:**

```JSON
{
	"ENV_VAR_1": "VALUE_1",
	"ENV_VAR_2": "VALUE_2",
	"ENV_VAR_3": "VALUE_3"
}
```

### [`show backend`](https://cbonte.github.io/haproxy-dconv/1.7/management.html#9.3-show%20backend)

#### URL Structure

```
.../hapra/show/backend
```

**Socket Output:**

```sh
backend-0
backend-1
backend-2
```

**Successful API Call Output:**

```JSON
{
	"0": "backend-0",
	"1": "backend-1",
	"2": "backend-2"
}
```
