package com.v2ray.ang.ui.main

// Permission dialogs and brief trips to another activity can produce consecutive onStart callbacks.
internal fun shouldRefreshSubscriptionsOnOpen(now: Long, lastAttempt: Long?, inFlight: Boolean): Boolean =
    !inFlight && (lastAttempt == null || now < lastAttempt || now - lastAttempt >= 10_000L)
