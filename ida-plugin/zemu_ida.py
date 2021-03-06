'''

Copyright (c) 2019 Zeropoint Dynamics, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

import idc
import idaapi

class ApplyZemuOverlay(idaapi.action_handler_t):
    '''
    Applies the overlay from the user-selected overlay file.
    '''

    def __init__(self):
        idaapi.action_handler_t.__init__(self)

    def activate(self, ctx):
        import json

        filepath = idc.AskFile(False, '*.zmu;*.overlay;*',
            'Load Zemu Overlay...')
        if filepath is None:
            return
        f = open(filepath, 'r')
        zemu_data = f.read()
        f.close()

        zemu_data = zemu_data[len('DISAS\n'):]
        zemu_dump = json.loads(zemu_data)

        # Apply the overlay data
        for comment in zemu_dump['comments']:
            ea = comment['address']
            comment_text = str(comment['text'])
            color = comment.get('color', 0x73f0df)

            # Set color of instruction line
            idaapi.set_item_color(ea, color)
            idaapi.set_cmt(ea, comment_text, False)

            # Set function name if not already changed
            idc.GetFunctionAttr(ea, idc.FUNCATTR_START)
            name = idc.GetFunctionName(ea)
            if len(name) > 0 and name.startswith('zmu_') == False:
                idc.MakeName(ea, 'zmu_' + name)

        return 1

    def update(self, ctx):
        return idaapi.AST_ENABLE_ALWAYS


class zemuoverlay_t(idaapi.plugin_t):
    '''
    Adds a Zemu {View} menu option for loading an overlay.
    '''
    flags = 0
    comment = 'Load an overlay file generated by zemu.'
    help = comment
    wanted_name = 'ZemuOverlay'
    wanted_hotkey = ''
    menu_name = 'View/'
    menu_context = []

    def init(self):
        zemu_overlay_action = idaapi.action_desc_t(
            'zemuoverlay:action', 'Load Zemu Overlay...',
            ApplyZemuOverlay(), '', 'Load Zemu Overlay...', 199)

        idaapi.register_action(zemu_overlay_action)
        idaapi.attach_action_to_menu(
            'View/', 'zemuoverlay:action', idaapi.SETMENU_APP)

        return idaapi.PLUGIN_KEEP

    def term(self):
        pass

    def run(self, arg):
        pass

def PLUGIN_ENTRY():
    return zemuoverlay_t()
