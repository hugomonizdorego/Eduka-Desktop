// Menu of the login screen, opened above the bottom bar.
// items: [{ text, checked, enabled, icon }]; picked(index) when one is chosen.
import QtQuick 2.15

Rectangle {
    id: menu
    property var theme
    property string title: ""
    property string note: ""
    property var items: []
    property real anchorX: 0
    property real bottomY: 0
    property real widest: 0
    signal picked(int index)

    width: Math.max(220 * theme.s, Math.min(360 * theme.s, widest + 24 * theme.s))
    height: Math.min(content.implicitHeight + 20 * theme.s, bottomY - 12)
    x: Math.max(12, Math.min(parent.width - width - 12, anchorX))
    y: bottomY - height - 8 * theme.s
    radius: 18 * theme.s
    color: theme.contrast ? "#000000" : (theme.dark ? "#f2202322" : "#fafdfcfb")
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
                        width: list.width; height: 38 * menu.theme.s; radius: height / 2
                        property bool usable: modelData.enabled === undefined || modelData.enabled
                        color: rowArea.containsMouse && usable ? (menu.theme.contrast ? "#333333" : menu.theme.hoverColor) : (modelData.checked ? (menu.theme.contrast ? "#1affffff" : menu.theme.hoverColor) : "transparent")
                        border.color: modelData.checked ? menu.theme.accent : "transparent"; border.width: modelData.checked ? 1 : 0
                        opacity: usable ? 1 : 0.5
                        Icon {
                            id: rowIcon
                            anchors.left: parent.left; anchors.leftMargin: 12 * menu.theme.s; anchors.verticalCenter: parent.verticalCenter
                            width: 16 * menu.theme.s; height: width
                            name: modelData.icon ? modelData.icon : (modelData.checked ? "check" : "")
                            ink: modelData.checked && !modelData.icon ? menu.theme.accent : menu.theme.textColor
                        }
                        Text {
                            id: rowText
                            anchors.left: rowIcon.right; anchors.leftMargin: 10 * menu.theme.s; anchors.right: parent.right; anchors.rightMargin: 12 * menu.theme.s
                            anchors.verticalCenter: parent.verticalCenter
                            text: modelData.text; elide: Text.ElideRight
                            color: menu.theme.textColor; font.pixelSize: 14 * menu.theme.s; font.bold: modelData.checked === true
                            Component.onCompleted: menu.widest = Math.max(menu.widest, implicitWidth + 60 * menu.theme.s)
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
