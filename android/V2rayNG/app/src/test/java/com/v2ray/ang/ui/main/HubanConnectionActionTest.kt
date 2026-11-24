package com.v2ray.ang.ui.main

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class HubanConnectionActionTest {
    @Test fun `start without a subscription opens import`() {
        assertEquals(HubanConnectionAction.IMPORT, hubanConnectionAction(false, false, false))
    }

    @Test fun `a node selected in another subscription requires a new selection`() {
        assertEquals(HubanConnectionAction.SELECT_NODE, hubanConnectionAction(false, true, false))
    }

    @Test fun `a selected node in the visible subscription can start`() {
        assertEquals(HubanConnectionAction.START, hubanConnectionAction(false, true, true))
    }

    @Test fun `a running VPN can always stop even after changing subscription`() {
        assertEquals(HubanConnectionAction.STOP, hubanConnectionAction(true, true, false))
        assertEquals(HubanConnectionAction.STOP, hubanConnectionAction(true, false, false))
    }
}
