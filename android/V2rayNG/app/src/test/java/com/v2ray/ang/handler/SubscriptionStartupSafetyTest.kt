package com.v2ray.ang.handler

import com.v2ray.ang.dto.entities.SubscriptionCache
import com.v2ray.ang.dto.entities.SubscriptionItem
import kotlinx.coroutines.CancellationException
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class SubscriptionStartupSafetyTest {
    private val requested = SubscriptionItem(remarks = "QA", url = "https://example.com/sub")

    @Test fun `unchanged subscription can publish its response`() {
        assertTrue(AngConfigManager.canPublishSubscriptionRefresh(requested, requested.copy()))
    }

    @Test fun `deleted disabled edited or newer subscription cannot publish a stale response`() {
        val changed = listOf(
            null, requested.copy(enabled = false), requested.copy(url = "https://example.com/new"),
            requested.copy(requestHeaders = "new headers"), requested.copy(userAgent = "new agent"),
            requested.copy(filter = "new filter"), requested.copy(autoUpdate = true),
            requested.copy(lastUpdated = 1234), requested.copy(remarks = "new name")
        )
        changed.forEach { latest -> assertFalse(AngConfigManager.canPublishSubscriptionRefresh(requested, latest)) }
    }

    @Test fun `disabled subscription skips before any network or storage access`() {
        assertEquals(1, AngConfigManager.updateConfigViaSub(SubscriptionCache("qa", requested.copy(enabled = false))).skipCount)
    }

    @Test fun `cancelled startup propagates cancellation before any network or storage access`() {
        assertThrows(CancellationException::class.java) {
            AngConfigManager.updateConfigViaSub(SubscriptionCache("qa", requested)) { throw CancellationException("screen closed") }
        }
    }
}
