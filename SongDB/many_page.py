from discord import Embed, Interaction
from discord.ext.ui import (
    InteractionProvider,
    Message,
    PageView,
    PaginationView,
    View,
    ViewTracker,
)


class Page(PageView):
    def __init__(self, embeds: list[Embed]):
        super(Page, self).__init__()
        self.embeds = embeds

    async def body(self, _paginator: PaginationView) -> Message | View:
        return Message(embeds=self.embeds)

    async def on_appear(self, paginator: PaginationView) -> None:
        # print(f"appeared page: {paginator.page}")
        pass


class PagePage:
    def __init__(self, embeds: list[Embed]) -> None:
        self._embeds = embeds

    def _split(self, __embeds: list[Embed]) -> list[list[Embed]]:
        return [__embeds[num : num + 3] for num in range(0, len(__embeds), 3)]

    def _view(self) -> PaginationView:
        embed_list = self._split(self._embeds)
        pages = [Page(em) for em in embed_list]
        view = PaginationView(views=pages)
        return view

    async def _send(self, interaction: Interaction):
        view = self._view()
        tracker = ViewTracker(view, timeout=None)
        await tracker.track(InteractionProvider(interaction))
