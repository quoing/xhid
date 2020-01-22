from evdev import ecodes as ec

translate_tables = {}
translate_tables['default'] = {} # this will be empty for now
translate_tables['table1'] = {   # this table will translate some windows key codes to evdev
        # 256: ec.KEY_PLAYPAUSE, # seems that 256 denotes we need extra reading from KeyID (all media control keys have same code)
        284: ec.KEY_KPENTER,
        285: ec.KEY_RIGHTCTRL,
        309: ec.KEY_KPSLASH,
        311: ec.KEY_SYSRQ,
        327: ec.KEY_HOME,
        328: ec.KEY_UP,
        329: ec.KEY_PAGEUP,
        331: ec.KEY_LEFT,
        333: ec.KEY_RIGHT,
        335: ec.KEY_END,
        336: ec.KEY_DOWN,
        337: ec.KEY_PAGEDOWN,
        338: ec.KEY_INSERT,
        339: ec.KEY_DELETE,
        347: ec.KEY_LEFTMETA,
        348: ec.KEY_RIGHTMETA,
        }

