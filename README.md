# sakamatabot

![GitHub commit activity](https://img.shields.io/github/commit-activity/m/sushi-chaaaan/sakamata-alpha-pycord?style=flat-square)
[![CodeFactor](https://www.codefactor.io/repository/github/sushi-chaaaan/sakamata-alpha-pycord/badge)](https://www.codefactor.io/repository/github/sushi-chaaaan/sakamata-alpha-pycord)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dispanderfixed?style=flat-square)](https://www.python.org/downloads/release/python-3101/)
[![PyPI](https://img.shields.io/badge/pycord-2.0.0a-orange?style=flat-square)](https://github.com/Pycord-Development/pycord)
[![iroiro](https://img.shields.io/badge/discord--ext--ui-3.1.3-orange?style=flat-square)](https://github.com/sizumita/discord-ext-ui)
![Discord](https://img.shields.io/discord/915910043461890078?color=blueviolet&label=Discord&logo=Discord&logoColor=white&style=flat-square)

### このリポジトリは？
ホロライブ所属VTuber沙花叉クロヱさんの非公式ファンDiscordサーバー<br>
[「クロヱ水族館」](https://discord.gg/EqfjtNBf2M)の運営/管理補助を行うBotのコードです。<br>
テスト環境がクラウド上にあるため、Commitが多くなっています。

### 開発環境及び使用ライブラリ
Python 3.10.2<br>
[pycord](https://github.com/Pycord-Development/pycord) 2.0.0b4<br>
[discord-ext-ui](https://pypi.org/project/discord-ext-ui/) 3.1.3<br>
[dispander](https://github.com/sushi-chaaaan/dispanderfixed/tree/for2.0)([DiscordBotPortalJP様のライブラリ](https://github.com/DiscordBotPortalJP/dispander)をforkさせていただきました)<br>

### 各ブランチ
Mainブランチ:クロヱ水族館の本番環境<br>
alphaブランチ:バックアップ用。安定したコードしか上がりません。<br>
その他:マジの開発中ブランチ<br>


### 機能追加履歴

> v1.5.1(2022.02.21)

メッセージ送信機能の改善<br>
細かいバグ修正や最適化<br>
不要な機能の廃止<br>
歌枠データベース提供準備<br>

> v1.5.0(2022.02.11)

ファイル構造の見直し<br>

> v1.3.4(2022.02.09)

Modalのリリースに伴い配信登録コマンドをModalへ移行<br>
Modalを利用したサーバー内問い合わせ/目安箱機能を実装<br>
その他細かいバグ修正<br>

> v1.3.3(2022.01.28)

ミニゲーム「Concept」が遊べるように<br>
メンバーシップ認証のフローがわかりやすくなった<br>
その他細かい最適化・修正<br>

> v.1.3.2(2022.01.25)

/user コマンドのデザイン変更<br>
スレッド一覧生成コマンド<br>
配信通知機能を停止

> v1.3.1(2022.01.24)

MessageCommandの上限に達したため翻訳をTransCordへ移行

> v1.3.0(2022.01.23)

配信通知機能のアップデート<br>
右クリックによる翻訳・ピン留めに対応<br>
投票機能の更新<br>
StarBoard機能のテスト<br>
濁点を付けて自慢する機能の追加<br>
スローモードの右クリックON/OFF<br>

> v1.2.1(2022.01.14)

Discordによる破壊的変更に対応するためBotのPrefixを`//`へ変更<br>

> v1.2.0(2022.01.10)

[holodex](https://pypi.org/project/holodex/0.9.7/) 0.9.7を利用した配信枠検知<br>
メンバーシップの継続や継続停止の際のメンバーシップコマンド<br>
timeoutへの対応<br>
配信のイベント登録の簡略化<br>
投票機能<br>

> v1.1.1(2022.01.03)

[pycord](https://github.com/Pycord-Development/pycord)へ移行<br>
[discord-ext-ui](https://pypi.org/project/discord-ext-ui/)を導入<br>
メッセージ展開の処理を改善<br>
メンバーシップ認証機能をブラッシュアップ<br>
ユーザー情報取得機能をブラッシュアップ<br>

> v1.1.0(2022.01.02)

確認を必要とするコマンドの処理の最適化<br>
メンバーシップ認証用コマンドを追加<br>
メッセージ展開の処理を改善

> v1.0.7(2021.12.31)

NGワード検知機能を強化<br>
自身のサーバー以外の招待URLを検知可能に<br>

> v1.0.6(2021.12.27)

NGワード検知機能を追加<br>

> v.1.0.5(2021.12.26)

コマンドごとの承認機能を追加<br>
コマンドを権限ごとにコントロール<br>
メッセージリンク展開の仕様変更<br>

> v1.0.4(2021.12.25)

不要な部分の最適化<br>
メッセージ送信/編集機能の追加<br>
エラー転送機能の実装<br>
実行ログ機能の実装<br>
VCログ機能のアップデート<br>

> v1.0.3(2021.12.19)

DM送受信機能/ping機能/user情報取得機能の追加<br>

> v1.0.2(2021.12.7)

メッセージ展開の処理を改善<br>

> v1.0.1(2021.12.5)

VCログの成形を改善<br>

> v1.0.0(2021.12.5)

Dispanderによるメッセージリンク展開に対応<br>
VCのログをユーザーID形式で保存する機能を追加<br>

