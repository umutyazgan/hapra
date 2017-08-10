TODO:
=====
 - [ ] Add command line parameters other than table name for `clear table` command
 - [ ] `shutdown session <session>` and `shutdown sessions server <backend/server>` does not seem to shutdown anything even though shutdown command is correct.
 - [ ] Add error handling mechanisms and HTTP status codes.
 - [ ] Need to generate some kind of error in order to implement `show errors` command
 - [ ] All `map` and `acl` commands will be implemented later
 - [ ] Outputs of `show sess` and `show sess <id>` commands are difficult to parse into JSON. Going to deal with them later.
 - [ ] Need resolvers in config file in order to implement `show stat resolvers` command
 - [ ] `show table` command works but takes no parameters and hasn't been tested with different tables.
 - [ ] Need to set up TLS keys in order to implement `show tls-keys` command
 - [x] `shutdown` commands require admin rights. Need to find a way to implement them.
