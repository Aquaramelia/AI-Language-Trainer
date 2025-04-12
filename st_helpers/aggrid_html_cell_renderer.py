HtmlCellRenderer = """ class HtmlCellRenderer {
    init(params) {
        this.params = params;
        this.eGui = document.createElement('div');
        
        if (!document.getElementById('google-font-style')) {
            const style = document.createElement('style');
            style.id = 'google-font-style';
            style.innerHTML = `
                @import url("https://fonts.googleapis.com/css2?family=Delius:wght@300;400;600&display=swap");
                .custom-font {
                    font-family: 'Delius' !important;
                }
            `;
            document.head.appendChild(style);
        }

        this.eGui.innerHTML = `
            <span class="custom-font">
                <b>${this.params.value}</b>
            </span>
        `;
    }

    getGui() {
        return this.eGui;
    }

    refresh(params) {
        this.params = params;
        this.eGui.innerHTML = `<span class="custom-font"><b>${this.params.value}</b></span>`;
        return true;
    }

    refreshTable(value) {
        this.params.setValue(value);
    }
}
 """