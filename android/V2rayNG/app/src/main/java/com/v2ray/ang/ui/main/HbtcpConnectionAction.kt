package com.v2ray.ang.ui.main

internal enum class HbtcpConnectionAction { START, STOP, IMPORT, SELECT_NODE }

/** A selection in another subscription must never silently start that subscription's node. */
internal fun hbtcpConnectionAction(running: Boolean, hasNodes: Boolean, selectionInGroup: Boolean): HbtcpConnectionAction =
    when {
        running -> HbtcpConnectionAction.STOP
        !hasNodes -> HbtcpConnectionAction.IMPORT
        !selectionInGroup -> HbtcpConnectionAction.SELECT_NODE
        else -> HbtcpConnectionAction.START
    }
