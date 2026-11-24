package com.v2ray.ang.ui.main

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class HbtcpConnectionActionTest {
    @Test fun `start without a subscription opens import`() {
        assertEquals(HbtcpConnectionAction.IMPORT, hbtcpConnectionAction(false, false, false))
    }

    @Test fun `a node selected in another subscription requires a new selection`() {
        assertEquals(HbtcpConnectionAction.SELECT_NODE, hbtcpConnectionAction(false, true, false))
    }

    @Test fun `a selected node in the visible subscription can start`() {
        assertEquals(HbtcpConnectionAction.START, hbtcpConnectionAction(false, true, true))
    }

    @Test fun `a running VPN can always stop even after changing subscription`() {
        assertEquals(HbtcpConnectionAction.STOP, hbtcpConnectionAction(true, true, false))
        assertEquals(HbtcpConnectionAction.STOP, hbtcpConnectionAction(true, false, false))
    }
}
