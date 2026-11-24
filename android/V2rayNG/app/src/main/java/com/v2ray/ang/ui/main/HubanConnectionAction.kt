package com.v2ray.ang.ui.main

internal enum class HubanConnectionAction { START, STOP, IMPORT, SELECT_NODE }

/** A selection in another subscription must never silently start that subscription's node. */
internal fun hubanConnectionAction(running: Boolean, hasNodes: Boolean, selectionInGroup: Boolean): HubanConnectionAction =
    when {
        running -> HubanConnectionAction.STOP
        !hasNodes -> HubanConnectionAction.IMPORT
        !selectionInGroup -> HubanConnectionAction.SELECT_NODE
        else -> HubanConnectionAction.START
    }
