// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2026 Hugo Moniz do Rego and the Edukasaun OS contributors
// Menu of the login screen, opened next to the field or button it belongs to.
// items: [{ text, sub, checked, enabled, icon }]; picked(index) when one is chosen.
// side: "below" (above when there is no room below) or "left" (beside the rail).
import QtQuick 2.15

Rectangle {
    id: menu
    property var theme
    property Item anchorItem: null
    property string side: "below"
    property real minWidth: 0
    property string title: ""
    property string note: ""
    property var items: []
    property real widest: 0
    // Where the anchor is, in the coordinates of the menu's parent (set on opening).
    property real ax: 0
    property real ay: 0
    property real aw: 0
    property real ah: 0
    signal picked(int index)

    readonly property real gap: 8 * theme.s
    readonly property real wanted: content.implicitHeight + 20 * theme.s
    readonly property bool roomBelow: ay + ah + gap + wanted <= parent.height - 12
    readonly property bool below: roomBelow || ay + ah / 2 < parent.height / 2

    function place() {
        if (!anchorItem) return
        var p = anchorItem.mapToItem(menu.parent, 0, 0)
        ax = p.x; ay = p.y; aw = anchorItem.width; ah = anchorItem.height
    }
    onVisibleChanged: if (visible) place()

    width: Math.max(minWidth, 230 * theme.s, Math.min(380 * theme.s, widest + 24 * theme.s))
    height: Math.max(48 * theme.s, Math.min(wanted, side === "left" ? parent.height - 24
                                                                    : (below ? parent.height - (ay + ah + gap) - 12 : ay - gap - 12)))
    x: side === "left" ? Math.max(12, ax - width - gap)
                       : Math.max(12, Math.min(parent.width - width - 12, ax + (aw - width) / 2))
    y: side === "left" ? Math.max(12, Math.min(parent.height - height - 12, ay + ah / 2 - height / 2))
                       : (below ? ay + ah + gap : ay - gap - height)
    radius: 18 * theme.s
    color: theme.contrast ? "#000000" : theme.menuColor
    border.color: theme.contrast ? "#ffffff" : (theme.dark ? "#33ffffff" : "#1a000000"); border.width: theme.contrast ? 2 : 1
    clip: true
    // Clicks inside the menu never reach the area that closes it.
    MouseArea { anchors.fill: parent }

    Flickable {
        anchors.fill: parent; anchors.margins: 10 * menu.theme.s
        contentHeight: content.implicitHeight
        interactive: contentHeight > height
        clip: true
        Column {
            id: content
            width: parent.width
            spacing: 2 * menu.theme.s
            Text {
                visible: menu.title.length > 0
                text: menu.title
                leftPadding: 10 * menu.theme.s; topPadding: 2 * menu.theme.s; bottomPadding: 4 * menu.theme.s
                color: menu.theme.subColor; font.pixelSize: 12 * menu.theme.s; font.bold: true
            }
            Column {
                id: list
                width: parent.width
                Repeater {
                    model: menu.items
                    delegate: Rectangle {
                        width: list.width; height: 40 * menu.theme.s; radius: height / 2
                        property bool usable: modelData.enabled === undefined || modelData.enabled
                        color: rowArea.containsMouse && usable ? (menu.theme.contrast ? "#333333" : menu.theme.hoverColor) : (modelData.checked ? (menu.theme.contrast ? "#1affffff" : menu.theme.hoverColor) : "transparent")
                        border.color: modelData.checked ? menu.theme.accent : "transparent"; border.width: modelData.checked ? 1 : 0
                        opacity: usable ? 1 : 0.5
                        Accessible.role: Accessible.MenuItem
                        Accessible.name: modelData.text
                        Icon {
                            id: rowIcon
                            anchors.left: parent.left; anchors.leftMargin: 12 * menu.theme.s; anchors.verticalCenter: parent.verticalCenter
                            width: 16 * menu.theme.s; height: width
                            name: modelData.icon ? modelData.icon : (modelData.checked ? "check" : "")
                            ink: modelData.checked ? menu.theme.accent : menu.theme.textColor
                        }
                        Text {
                            id: rowSub
                            anchors.right: parent.right; anchors.rightMargin: 14 * menu.theme.s
                            anchors.verticalCenter: parent.verticalCenter
                            visible: text.length > 0
                            text: modelData.sub ? modelData.sub : ""
                            color: menu.theme.subColor; font.pixelSize: 12 * menu.theme.s
                        }
                        Text {
                            id: rowText
                            anchors.left: rowIcon.right; anchors.leftMargin: 10 * menu.theme.s
                            anchors.right: rowSub.visible ? rowSub.left : parent.right; anchors.rightMargin: 12 * menu.theme.s
                            anchors.verticalCenter: parent.verticalCenter
                            text: modelData.text; elide: Text.ElideRight
                            color: menu.theme.textColor; font.pixelSize: 14 * menu.theme.s; font.bold: modelData.checked === true
                            Component.onCompleted: menu.widest = Math.max(menu.widest, implicitWidth + rowSub.implicitWidth + 70 * menu.theme.s)
                        }
                        MouseArea {
                            id: rowArea
                            anchors.fill: parent; hoverEnabled: true
                            cursorShape: usable ? Qt.PointingHandCursor : Qt.ArrowCursor
                            onClicked: if (usable) menu.picked(index)
                        }
                    }
                }
            }
            Text {
                visible: menu.note.length > 0
                width: parent.width
                text: menu.note; wrapMode: Text.WordWrap
                leftPadding: 10 * menu.theme.s; rightPadding: 10 * menu.theme.s; topPadding: 6 * menu.theme.s
                color: menu.theme.subColor; font.pixelSize: 11 * menu.theme.s
            }
        }
    }
}
