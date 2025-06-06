import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15

ApplicationWindow {
    visible: true
    width: 500
    height: 600
    title: "PDF Sign & Verify"
    Material.theme: Material.Light
    Material.accent: Material.Teal

    signal selectPdf()
    signal selectPublicKey()
    signal signPdf()
    signal verifyPdf()

    property bool usbConnected: false
    property bool privateKeyLoaded: false
    property bool publicKeyLoaded: false
    property bool pdfFileLoaded: false
    property bool signingInProgress: false
    property bool verificationInProgress: false

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 16

        Label {
            text: "PDF Signature Manager"
            font.pixelSize: 24
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Rectangle {
                id: privateKeyIndicator
                width: 16
                height: 16
                radius: 8
                color: (privateKeyLoaded && usbConnected) ? "green" : (usbConnected ? "blue" : "red")
                border.color: "#444"
                border.width: 1
            }

            Label {
                text: (privateKeyLoaded && usbConnected) ? "Signing key loaded" : 
                    (usbConnected ? "USB connected. Loading  signing key..." : 
                    "Signing key not loaded. Connect USB device with the key.")
                font.pixelSize: 14
                color: "#333"
            }
        }

        Label {
            id: selectedPdfLabel
            text: "No PDF file selected"
            wrapMode: Text.Wrap
            Layout.fillWidth: true
        }

        Button {
            text: pdfFileLoaded ? "Cancel" : "Select PDF File"
            Layout.fillWidth: true
            onClicked: selectPdf() 
            Material.background: pdfFileLoaded ? Material.Red : Material.Gray
            Material.foreground: pdfFileLoaded ? "white" : "black"
        }

        Label {
            id: selectedKeyLabel
            text: "No key selected"
            wrapMode: Text.Wrap
            Layout.fillWidth: true
        }

        Button {
            text: publicKeyLoaded ? "Cancel" : "Select Verification Key"
            Layout.fillWidth: true
            onClicked: selectPublicKey()
            Material.background: publicKeyLoaded ? Material.Red : Material.Gray
            Material.foreground: publicKeyLoaded ? "white" : "black"
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            // SIGN PDF BUTTON WITH TOOLTIP
            Item {
                Layout.fillWidth: true
                Layout.preferredWidth: 1  // Makes both buttons take equal width
                height: signButton.implicitHeight

                Button {
                    id: signButton
                    text: signingInProgress ? "Signing..." : "Sign PDF"
                    anchors.fill: parent
                    enabled: privateKeyLoaded && pdfFileLoaded && !signingInProgress
                    Material.background: Material.Teal
                    Material.foreground: "white"
                    onClicked: signPdf()
                }

                ToolTip.visible: !signButton.enabled && signTipArea.containsMouse
                ToolTip.text: !privateKeyLoaded
                            ? "Connect a USB device to enable signing"
                            : "Select a PDF file to enable signing"

                MouseArea {
                    id: signTipArea
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.NoButton
                }
            }

            // VERIFY SIGNATURE BUTTON WITH TOOLTIP
            Item {
                Layout.fillWidth: true
                Layout.preferredWidth: 1
                height: verifyButton.implicitHeight

                Button {
                    id: verifyButton
                    text: verificationInProgress ? "Verifying..." : "Verify Signature"
                    anchors.fill: parent
                    enabled: pdfFileLoaded && publicKeyLoaded && !verificationInProgress
                    Material.background: Material.Blue
                    Material.foreground: "white"
                    onClicked: verifyPdf()
                }

                ToolTip.visible: !verifyButton.enabled && verifyTipArea.containsMouse
                ToolTip.text: publicKeyLoaded
                            ? "Select a PDF file to enable verification"
                            : "Select a verification key"

                MouseArea {
                    id: verifyTipArea
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.NoButton
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 120
            color: "#f5f5f5"
            radius: 8
            border.color: "#cccccc"
            border.width: 1

            ScrollView {
                anchors.fill: parent
                TextArea {
                    id: outputLog
                    text: "Status messages will appear here..."
                    wrapMode: Text.Wrap
                    readOnly: true
                    background: null
                }
            }
        }
    }

    // These functions are called from Python
    function setPdfFile(path) {
        selectedPdfLabel.text = path
    }

    function setPublicKeyFile(path) {
        selectedKeyLabel.text = path
    }

    function append_log(message) {
        outputLog.text += "\n" + message
    }
}
