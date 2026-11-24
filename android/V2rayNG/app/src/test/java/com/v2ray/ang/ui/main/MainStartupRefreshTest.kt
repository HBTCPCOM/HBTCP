package com.v2ray.ang.ui.main

import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class MainStartupRefreshTest {
    @Test fun `first open refreshes`() = assertTrue(shouldRefreshSubscriptionsOnOpen(0, null, false))
    @Test fun `concurrent foreground callbacks reuse running refresh`() = assertFalse(shouldRefreshSubscriptionsOnOpen(30_000, 0, true))
    @Test fun `return from permission dialog does not issue a duplicate request`() = assertFalse(shouldRefreshSubscriptionsOnOpen(9_999, 0, false))
    @Test fun `later foreground open refreshes again`() = assertTrue(shouldRefreshSubscriptionsOnOpen(10_000, 0, false))
    @Test fun `reset elapsed clock permits refresh`() = assertTrue(shouldRefreshSubscriptionsOnOpen(0, 30_000, false))
}
