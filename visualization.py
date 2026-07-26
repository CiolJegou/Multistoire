import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib import colormaps


class ArbreInteractif:

    def __init__(
        self,
        tree,
        single_value,
        complete_value,
        preview_length=300
    ):

        self.tree = tree
        self.single_value = single_value
        self.complete_value = complete_value

        self.preview_length = preview_length

        # --------------------------------------------------
        # Tous les nœuds
        # --------------------------------------------------

        self.nodes = self.get_all_nodes()

        # --------------------------------------------------
        # Profondeur de chaque nœud
        # --------------------------------------------------

        self.depths = self.compute_depths()

        # --------------------------------------------------
        # Position des nœuds
        # --------------------------------------------------

        self.pos = self.compute_tree_layout()

        # --------------------------------------------------
        # État courant
        # --------------------------------------------------

        self.selected_node = None

        # Axes des boutons du panneau droit
        self.detail_button_axes = []

        # Objets Button
        self.child_buttons = []

        # --------------------------------------------------
        # Figure
        # --------------------------------------------------

        self.fig = plt.figure(
            figsize=(16, 9)
        )

        # --------------------------------------------------
        # Panneau gauche
        # --------------------------------------------------

        self.ax_tree = self.fig.add_axes([
            0.03,
            0.08,
            0.62,
            0.84
        ])

        # --------------------------------------------------
        # Panneau droit
        # --------------------------------------------------

        self.ax_detail = self.fig.add_axes([
            0.70,
            0.08,
            0.27,
            0.84
        ])

        # --------------------------------------------------
        # Clics sur l'arbre
        # --------------------------------------------------

        self.fig.canvas.mpl_connect(
            "button_press_event",
            self.on_click
        )

        # --------------------------------------------------
        # Affichage initial
        # --------------------------------------------------

        self.draw_global_tree()

        self.draw_empty_detail_panel()

    # ======================================================
    # STRUCTURE
    # ======================================================

    def get_all_nodes(self):

        nodes = set()

        for parent, children in self.tree.items():

            nodes.add(parent)

            nodes.update(children)

        nodes.update(
            self.single_value.keys()
        )

        nodes.update(
            self.complete_value.keys()
        )

        return nodes

    def get_roots(self):

        all_nodes = set(self.nodes)

        children = set()

        for child_set in self.tree.values():

            children.update(child_set)

        return all_nodes - children

    # ======================================================
    # PROFONDEUR DES NŒUDS
    # ======================================================

    def compute_depths(self):

        depths = {}

        roots = sorted(
            self.get_roots(),
            key=str
        )

        visited = set()

        def visit(node, depth):

            # Si le nœud a déjà été atteint par un autre chemin
            if node in visited:

                return

            visited.add(node)

            depths[node] = depth

            children = sorted(
                self.tree.get(node, set()),
                key=str
            )

            for child in children:

                visit(
                    child,
                    depth + 1
                )

        for root in roots:

            visit(
                root,
                0
            )

        return depths

    # ======================================================
    # LAYOUT
    # ======================================================

    def compute_tree_layout(self):

        positions = {}

        roots = sorted(
            self.get_roots(),
            key=str
        )

        next_x = [0]

        visited = set()

        def visit(node, depth):

            if node in visited:

                return positions[node][0]

            visited.add(node)

            children = sorted(
                self.tree.get(node, set()),
                key=str
            )

            # Feuille
            if not children:

                x = next_x[0]

                next_x[0] += 1

                positions[node] = (
                    x,
                    -depth
                )

                return x

            child_x_positions = []

            for child in children:

                child_x = visit(
                    child,
                    depth + 1
                )

                child_x_positions.append(
                    child_x
                )

            x = sum(
                child_x_positions
            ) / len(
                child_x_positions
            )

            positions[node] = (
                x,
                -depth
            )

            return x

        for root in roots:

            visit(
                root,
                0
            )

        return positions

    # ======================================================
    # COULEUR SELON LA PROFONDEUR
    # ======================================================

    def get_node_color(self, node):

        depth = self.depths.get(
            node,
            0
        )

        max_depth = max(
            self.depths.values(),
            default=1
        )

        # Normalisation de la profondeur
        normalized_depth = (
            depth / max_depth
            if max_depth > 0
            else 0
        )

        # Palette continue
        cmap = colormaps["viridis"]

        return cmap(
            normalized_depth
        )

    # ======================================================
    # ARBRE GLOBAL
    # ======================================================

    def draw_global_tree(self):

        self.ax_tree.clear()

        self.ax_tree.set_title(
            "Arbre global",
            fontsize=16
        )

        # --------------------------------------------------
        # Limites
        # --------------------------------------------------

        if self.pos:

            xs = [
                x
                for x, y in self.pos.values()
            ]

            ys = [
                y
                for x, y in self.pos.values()
            ]

            self.ax_tree.set_xlim(
                min(xs) - 1,
                max(xs) + 1
            )

            self.ax_tree.set_ylim(
                min(ys) - 1,
                max(ys) + 1
            )

        # --------------------------------------------------
        # Arêtes
        # --------------------------------------------------

        for parent, children in self.tree.items():

            if parent not in self.pos:

                continue

            x_parent, y_parent = self.pos[parent]

            for child in children:

                if child not in self.pos:

                    continue

                x_child, y_child = self.pos[child]

                self.ax_tree.plot(
                    [x_parent, x_child],
                    [y_parent, y_child],
                    linewidth=1.5,
                    zorder=1
                )

        # --------------------------------------------------
        # Nœuds
        # --------------------------------------------------

        for node, (x, y) in self.pos.items():

            is_selected = (
                node == self.selected_node
            )

            self.ax_tree.scatter(
                x,
                y,
                s=1200,
                color=self.get_node_color(node),
                edgecolors="red" if is_selected else "none",
                linewidths=3 if is_selected else 0,
                zorder=2
            )

            self.ax_tree.text(
                x,
                y,
                str(node),
                ha="center",
                va="center",
                fontsize=10,
                zorder=3
            )

        self.ax_tree.axis("off")

        self.fig.canvas.draw_idle()

    # ======================================================
    # SUPPRESSION DES ANCIENS BOUTONS
    # ======================================================

    def clear_detail_buttons(self):

        # Suppression des objets Button
        self.child_buttons.clear()

        # Suppression des axes matplotlib
        for ax in self.detail_button_axes:

            ax.remove()

        self.detail_button_axes.clear()

    # ======================================================
    # PANNEAU VIDE
    # ======================================================

    def draw_empty_detail_panel(self):

        # Très important :
        # supprimer les boutons précédents
        self.clear_detail_buttons()

        self.ax_detail.clear()

        self.ax_detail.text(
            0.5,
            0.5,
            "Cliquez sur un nœud\n"
            "dans l'arbre global",
            ha="center",
            va="center",
            fontsize=14,
            transform=self.ax_detail.transAxes
        )

        self.ax_detail.axis("off")

        self.fig.canvas.draw_idle()

    # ======================================================
    # PANNEAU DE DÉTAIL
    # ======================================================

    def draw_detail_panel(self, node):

        # --------------------------------------------------
        # SUPPRESSION DES ANCIENS BOUTONS
        # --------------------------------------------------

        self.clear_detail_buttons()

        # Nettoyage du panneau principal
        self.ax_detail.clear()

        # --------------------------------------------------
        # Données
        # --------------------------------------------------

        value = self.single_value.get(
            node,
            ""
        )

        children = sorted(
            self.tree.get(node, set()),
            key=str
        )

        # --------------------------------------------------
        # Titre
        # --------------------------------------------------

        self.ax_detail.text(
            0.5,
            0.96,
            f"Nœud : {node}",
            ha="center",
            va="center",
            fontsize=15,
            fontweight="bold",
            transform=self.ax_detail.transAxes
        )

        # --------------------------------------------------
        # Valeur
        # --------------------------------------------------

        self.ax_detail.text(
            0.02,
            0.87,
            "Valeur :",
            ha="left",
            va="top",
            fontsize=11,
            fontweight="bold",
            transform=self.ax_detail.transAxes
        )

        preview = self.make_preview(
            value
        )

        self.ax_detail.text(
            0.02,
            0.81,
            preview,
            ha="left",
            va="top",
            fontsize=10,
            wrap=True,
            transform=self.ax_detail.transAxes
        )

        # --------------------------------------------------
        # Bouton valeur complète
        # --------------------------------------------------

        button_ax = self.fig.add_axes([
            0.735,
            0.60,
            0.20,
            0.045
        ])

        self.detail_button_axes.append(
            button_ax
        )

        full_text_button = Button(
            button_ax,
            "Afficher la valeur complète"
        )

        full_text_button.on_clicked(
            lambda event:
            self.show_full_value(node)
        )

        self.child_buttons.append(
            full_text_button
        )

        # --------------------------------------------------
        # Liste des fils
        # --------------------------------------------------

        self.ax_detail.text(
            0.02,
            0.52,
            f"Fils ({len(children)}) :",
            ha="left",
            va="top",
            fontsize=11,
            fontweight="bold",
            transform=self.ax_detail.transAxes
        )

        if not children:

            self.ax_detail.text(
                0.02,
                0.44,
                "Aucun fils",
                ha="left",
                va="top",
                fontsize=10,
                transform=self.ax_detail.transAxes
            )

        else:

            button_height = 0.045

            first_y = 0.45

            spacing = 0.055

            for i, child in enumerate(children):

                y = first_y - i * spacing

                if y < 0.03:

                    break

                child_ax = self.fig.add_axes([
                    0.735,
                    y,
                    0.20,
                    button_height
                ])

                self.detail_button_axes.append(
                    child_ax
                )

                child_button = Button(
                    child_ax,
                    str(child)
                )

                child_button.on_clicked(
                    lambda event,
                    child=child:
                    self.select_node(child)
                )

                self.child_buttons.append(
                    child_button
                )

        self.ax_detail.axis("off")

        self.fig.canvas.draw_idle()

    # ======================================================
    # APERÇU
    # ======================================================

    def make_preview(self, value):

        value = str(value)

        if len(value) <= self.preview_length:

            return value

        return (
            value[:self.preview_length]
            + "\n\n[...]"
        )

    # ======================================================
    # FENÊTRE VALEUR COMPLÈTE
    # ======================================================

    def show_full_value(self, node):

        value = str(
            self.complete_value.get(
                node,
                ""
            )
        )

        text_window = plt.figure(
            figsize=(12, 8)
        )

        try:

            text_window.canvas.manager.set_window_title(
                f"Valeur complète — {node}"
            )

        except AttributeError:

            pass

        ax = text_window.add_axes([
            0.05,
            0.05,
            0.90,
            0.90
        ])

        ax.text(
            0,
            1,
            value,
            ha="left",
            va="top",
            fontsize=10,
            wrap=True
        )

        ax.axis("off")

        plt.show()

    # ======================================================
    # CLIC DANS L'ARBRE
    # ======================================================

    def on_click(self, event):

        if event.inaxes != self.ax_tree:

            return

        if event.xdata is None:

            return

        if event.ydata is None:

            return

        clicked_node = (
            self.find_clicked_global_node(
                event.xdata,
                event.ydata
            )
        )

        if clicked_node is not None:

            self.select_node(
                clicked_node
            )

    # ======================================================
    # DÉTECTION DU CLIC
    # ======================================================

    def find_clicked_global_node(
        self,
        x_click,
        y_click
    ):

        tolerance = 0.35

        for node, (x, y) in self.pos.items():

            distance = (
                (x_click - x) ** 2
                +
                (y_click - y) ** 2
            ) ** 0.5

            if distance < tolerance:

                return node

        return None

    # ======================================================
    # SÉLECTION
    # ======================================================

    def select_node(self, node):

        self.selected_node = node

        self.draw_global_tree()

        self.draw_detail_panel(
            node
        )

    # ======================================================
    # LANCEMENT
    # ======================================================

    def show(self):

        plt.show()


if __name__=='__main__':
    tree = {
        "A": {"B", "C"},
        "B": {"D", "E"},
        "C": {"F"},
        "D": set(),
        "E": set(),
        "F": set(),
    }


    single_value = {
        "A": "Résumé court de A",
        "B": "Résumé court de B",
        "C": "Résumé court de C",
        "D": "Résumé court de D",
        "E": "Résumé court de E",
        "F": "Résumé court de F",
    }


    complete_value = {
        "A": "Texte complet beaucoup plus long correspondant au nœud A...",
        "B": "Texte complet beaucoup plus long correspondant au nœud B...",
        "C": "Texte complet beaucoup plus long correspondant au nœud C...",
        "D": "Texte complet beaucoup plus long correspondant au nœud D...",
        "E": "Texte complet beaucoup plus long correspondant au nœud E...",
        "F": "Texte complet beaucoup plus long correspondant au nœud F...",
    }


    app = ArbreInteractif(
        tree=tree,
        single_value=single_value,
        complete_value=complete_value,
        preview_length=300
    )

    app.show()