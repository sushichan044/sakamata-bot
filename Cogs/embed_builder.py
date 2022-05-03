import discord
from discord import Embed


class EmbedBuilder:
    def __init__(self) -> None:
        pass

    @staticmethod
    def _concept_start_parent(parent: discord.Member) -> Embed:
        embed = Embed(
            title="Conceptへようこそ。",
            description=f"{parent.mention}さんは親に選ばれました。\n回答にする単語をこのメッセージに__返信__してください。",
            color=15767485,
        )
        return embed

    @staticmethod
    def _concept_start(parent: discord.Member) -> Embed:
        embed = Embed(
            title="Conceptへようこそ。",
            description=f"{parent.mention}さんが親に選ばれました。\n親が回答をセットするまで\nしばらくお待ちくさい。",
            color=15767485,
        )
        return embed

    @staticmethod
    def _concept_set_answer_embed(
        game_thread: discord.Thread, answer_word: str, master: discord.Member
    ) -> Embed:
        embed = Embed(
            title="回答をセットしました。",
            description=f"セットされた回答: {answer_word}\n\n{game_thread.mention}でゲームを開始してください。\n\n万が一回答に時間がかかりすぎた際は、\n{master.mention}さんが{game_thread.mention}に\n回答を送信することでゲームを終了できます。",
            color=15767485,
        )
        return embed

    @staticmethod
    def _concept_set_answer_embed_game() -> Embed:
        embed = Embed(
            title="親が回答をセットしました。",
            description="親がゲームを開始するまでお待ちください。",
            color=15767485,
        )
        return embed

    @staticmethod
    def _inquiry_contact(thread: discord.Thread) -> Embed:
        embed = Embed(
            title="スレッドが作成されました。",
            description="お問い合わせありがとうございます。\n下のスレッドリンクからスレッドへ移動して、\n内容の投稿をお願いします。",
            color=2105893,
        )
        embed.add_field(name="スレッド", value=thread.mention)
        return embed
