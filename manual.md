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
		"type": "beg",
		"case": "sensitive",
		"found": "yes",
		"idx": "tree",
		"key": "1",
		"value": "deneme1",
		"type": "str"
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

#### Output Format

**Socket Output:**

```sh
type=int, case=sensitive, match=yes, idx=list, pattern="1:"
```

**Successful API Call Output:**

```JSON
{
	"status": "success",
	"code": "200",
	"response": {
		"type": "int",
		"case": "sensitive",
		"match": "yes",
		"idx": "list",
		"pattern": "1:"
	}
}
```

### [`get weight <backend>/<server>`](https://cbonte.github.io/haproxy-dconv/1.7/management.html#9.3-get%20weight)

#### URL Structure

```
.../hapra/get/weight?backend=<backend>&server=<server>
```

* `backend`: name of the backend that contains the server
* `server`: name of the server that you want to get weight from

**Socket Output:**

```sh
1 (initial 1)
```

**Successful API Call Output:**

```JSON
{
	"weight": "1",
	"initial": "1"
}
```

### [`help`](https://cbonte.github.io/haproxy-dconv/1.7/management.html#9.3-help)

#### URL Structure

```
.../hapra/help
```

**Socket Output:**

```
  help           : this message
  prompt         : toggle interactive mode with prompt
  quit           : disconnect
  disable agent  : disable agent checks (use 'set server' instead)
  disable health : disable health checks (use 'set server' instead)
  disable server : disable a server for maintenance (use 'set server' instead)
  enable agent   : enable agent checks (use 'set server' instead)
  ...            : ...
```

**Successful API Call Output:**

```JSON
{
	"help": "this message",
	"prompt": "toggle interactive mode with prompt",
	"quit": "disconnect",
	"disable agent": "disable agent checks (use 'set server' instead)",
	"disable health": "disable health checks (use 'set server' instead)",
	"disable server": "disable a server for maintenance (use 'set server' instead)",
	"enable agent": "enable agent checks (use 'set server' instead)",
	"...": "..."
}
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

### [`show stat [{<iid>|<proxy>} <type> <sid>] [typed]`](https://cbonte.github.io/haproxy-dconv/1.7/management.html#9.3-show%20stat)

#### URL Structure

```
.../hapra/show/stat?iid=<iid>&type=<type>&sid=<sid>
```

* `iid`: A proxy ID. Use -1 to dump everything. Usage of proxy name instead of
		 ID is not tested therefore, not recommended.
* `type`: Type of dumpable objects. 1 for frontends, 2 for backends, 4 for
		  servers, -1 for everything. These values can be ORed like this:
		  1 + 2 = 3 for frontend + backend,
		  1 + 2 + 4 = 7 for frontend + backend + server.
* `sid`: Server ID. Use -1 to dump everything.

(You must run this command with either no arguments or all arguments. It won't
work when invoked with only 1 or 2 arguments)

**Socket Output:**

This method uses
[typed](https://cbonte.github.io/haproxy-dconv/1.7/management.html#9.2)
format instead of default CSV format.
```
F.2.0.0.pxname.1:KNS:str:haproxy3-monitoring
F.2.0.1.svname.1:KNS:str:FRONTEND
F.2.0.4.scur.1:MGP:u32:0
F.2.0.5.smax.1:MMP:u32:0
F.2.0.6.slim.1:CLP:u32:3000
F.2.0.7.stot.1:MCP:u64:0
F.2.0.8.bin.1:MCP:u64:0
F.2.0.9.bout.1:MCP:u64:0
...
B.2.0.0.pxname.1:KNS:str:haproxy3-monitoring
B.2.0.1.svname.1:KNS:str:BACKEND
B.2.0.2.qcur.1:MGP:u32:0
B.2.0.3.qmax.1:MMP:u32:0
B.2.0.4.scur.1:MGP:u32:0
B.2.0.5.smax.1:MMP:u32:0
B.2.0.6.slim.1:CLP:u32:300
B.2.0.7.stot.1:MCP:u64:0
B.2.0.8.bin.1:MCP:u64:0
...
```

**Successful API Call Output:**

```JSON
[
	{
		"type": "Frontend",
		"iid": "2",
		"sid": "0",
		"fields": [
			{
				"pno": "1",
				"pxname": "haproxy3-monitoring",
				"svname": "FRONTEND",
				"...": "..."
			},
			{
				"pno": "2",
				"pxname": "haproxy3-monitoring",
				"svname": "FRONTEND",
				"...": "..."
			},
			"..."
		]
	},
	{
		"type": "Backend",
		"iid": "2",
		"sid": "0",
		"fields": [
			{
				"pno": "1",
				"pxname": "haproxy3-monitoring",
				"svname": "BACKEND",
				"...": "..."
			}
			{
				"pno": "2",
				"pxname": "haproxy3-monitoring",
				"svname": "BACKEND",
				"...": "..."
			},
			"..."
		]
	},
	"..."
]
```
More explanation will be added for this output format.
<!--
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
-->
### [`show info [typed]`](https://cbonte.github.io/haproxy-dconv/1.7/management.html#9.3-show%20info)

#### URL Structure

```
.../hapra/show/info
```
(You must run this command with either no arguments or all arguments. It won't
work when invoked with only 1 or 2 arguments)

**Socket Output:**

This method uses
[typed](https://cbonte.github.io/haproxy-dconv/1.7/management.html#9.2)
format instead of default CSV format.
```
0.Name.1:POS:str:HAProxy
1.Version.1:POS:str:1.7.9-1ubuntu1
2.Release_date.1:POS:str:2017/09/14
3.Nbproc.1:CGS:u32:1
4.Process_num.1:KGP:u32:1
5.Pid.1:SGP:u32:1045
6.Uptime.1:MDP:str:0d 2h37m22s
7.Uptime_sec.1:MDP:u32:9442
8.Memmax_MB.1:CLP:u32:0
9.PoolAlloc_MB.1:MGP:u32:0
10.PoolUsed_MB.1:MGP:u32:0
...
```

**Successful API Call Output:**

```JSON
[
	{
		"pno": "1",
		"Name": "HAProxy",
		"Version": "1.7.9-1ubuntu1",
		"Release_date": "2017/09/14",
		"Nbproc": "1",
		"Process_num": "1",
		"...": "..."
	},
	{
		"pno": "2",
		"Name": "HAProxy",
		"Version": "1.7.9-1ubuntu1",
		"Release_date": "2017/09/14",
		"Nbproc": "1",
		"Process_num": "1",
		"...": "..."
	},
	"..."
]
```
More explanation will be added for this output format.

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

### [`show servers state`](https://cbonte.github.io/haproxy-dconv/1.7/management.html#9.3-show%20servers%20state)

#### URL Structure

```
.../hapra/show/servers-state?backend=<backend>
```

* `backend`: Backend name to limit output to desired backend only.

**Socket Output:**

```
# be_id be_name srv_id srv_name srv_addr srv_op_state srv_admin_state srv_uweight srv_iweight srv_time_since_last_change srv_check_status srv_check_result srv_check_health srv_check_state srv_agent_state bk_f_forced_id srv_f_forced_id
4 app-main 1 nginx1 172.17.0.2 0 0 1 1 10304 17 2 0 6 22 0 0
4 app-main 2 nginx2 172.17.0.3 0 0 1 1 10303 8 2 0 6 22 0 0
5 app-main2 1 nginx3 172.17.0.4 0 0 1 1 10303 8 2 0 6 22 0 0
```

**Successful API Call Output:**

```JSON
[
	{
		"be_id": "4",
		"be_name": "app-main",
		"srv_id": "1",
		"srv_name": "nginx1",
		"...": "..."
	},
	{
		"be_id": "4",
		"be_name": "app-main",
		"srv_id": "2",
		"srv_name": "nginx2",
		"...": "..."
	},
	"..."
]
```
