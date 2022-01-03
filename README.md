# sakamatabot

![GitHub commit activity](https://img.shields.io/github/commit-activity/m/sushi-chaaaan/sakamata-alpha-pycord?style=flat-square)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dispanderfixed?style=flat-square)](https://www.python.org/downloads/release/python-3101/)
[![PyPI](https://img.shields.io/badge/pycord-2.0.0a-orange?style=flat-square)](https://github.com/Pycord-Development/pycord)
[![PyPI](https://img.shields.io/badge/newdispanderfixed-0.1.4-orange?style=flat-square)](https://pypi.org/project/newdispanderfixed/)
![Discord](https://img.shields.io/discord/915910043461890078?color=blueviolet&label=Discord&logo=Discord&logoColor=white&style=flat-square)

### このリポジトリは？
ホロライブ所属VTuber沙花叉クロヱさんの非公式ファンDiscordサーバー[「クロヱ水族館」](https://discord.gg/EqfjtNBf2M)の運営/管理補助を行うBotのコードです。<br>
テスト環境がクラウド上にあるため、Commitが多くなっています。

### 開発環境及び使用ライブラリ
Python3.10.0<br>
[pycord 2.0.0a](https://github.com/Pycord-Development/pycord)<br>
[discord-ext-ui](https://pypi.org/project/discord-ext-ui/)<br>
newdispanderfixed 0.1.4([DiscordBotPortalJP様のライブラリ](https://github.com/DiscordBotPortalJP/dispander)をforkさせていただきました)<br>

### 各ブランチ
Mainブランチ:クロヱ水族館の本番環境<br>
alphaブランチ:バックアップ用。安定したコードしか上がりません。<br>
alpha-buttonブランチ:大規模改修を行うときに最初に書くブランチ。不安定なコードがコミットされます。<br>


### 機能追加履歴

> v1.1.1(2022.01.03)

pycordへ移行<br>
discord-ext-uiを導入<br>
メンバーシップ認証機能をブラッシュアップ
ユーザー情報取得機能をブラッシュアップ

> v1.1.0(2022.01.02)

確認を必要とするコマンドの処理の最適化<br>
メンバーシップ認証用コマンドを追加<br>
[dispanderfixed 0.3.0](https://pypi.org/project/dispanderfixed/0.3.0/)に更新し、埋め込みメッセージの複数枚の画像の処理を最適化

> v1.0.7(2021.12.31)

NGワード検知機能を強化。自身のサーバー以外の招待URｌを検知可能に。

> v1.0.6(2021.12.27)

NGワード検知機能を追加

> v.1.0.5(2021.12.26)

コマンドごとの承認機能を追加
コマンドを権限ごとにコントロール
メッセージリンク展開の仕様変更

> v1.0.4(2021.12.25)

不要な部分の最適化
メッセージ送信/編集機能の追加
エラー転送機能の実装
実行ログ機能の実装
VCログ機能のアップデート

> v1.0.3(2021.12.19)

DM送受信機能/ping機能/user情報取得機能の追加

> v1.0.2(2021.12.7)

使用ライブラリをdispander->dispanderfixedへ。
メッセージリンク展開の仕様を変更

> v1.0.1(2021.12.5)

VCログの成形を改善

> v1.0.0(2021.12.5)

Dispanderによるメッセージリンク展開に対応
VCのログをユーザーID形式で保存する機能を追加

