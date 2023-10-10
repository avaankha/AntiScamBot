import os
from dotenv import load_dotenv
import pytest
import pytest_asyncio
import discord.ext.test as dpytest
from BotEnums import BanLookup
from BotSetup import SetupDatabases
from DiscordBot import DiscordScamBot


@pytest_asyncio.fixture
async def bot() -> DiscordScamBot:

    # Setup of the bot to integrate with dpytest
    bot = DiscordScamBot()
    await bot._async_setup_hook()
    dpytest.configure(bot)
    yield bot

    # cleanup step where db file is removed
    bot.Database.Close()
    os.remove(os.getenv("DATABASE_FILE"))
    
"""
What's tested:
    - calling PrepareBan() with a new valid ban returns BanLookup.Banned
    - entry in db has matching data
    - calling PrepareBan() with the same ban return BanLookup.Duplicate
"""
@pytest.mark.asyncio
async def test_prepare_ban(bot: DiscordScamBot):

    # ban target needs to be a member of the first test guild in order for the http mock to have access to it
    banne_name = "Ban target"
    banne_id = 12345
    test_ban_target = dpytest.backend.make_user(banne_name, discrim=4, id_num=banne_id)
    banne_member = await dpytest.member_join(0, test_ban_target)

    # setup for the member object but we only need member.name and member.id
    banner_name = "Banner"
    banner_id = 123456
    test_banner = dpytest.backend.make_user(banner_name, discrim=5, id_num=banner_id)
    banner_member = await dpytest.member_join(0, test_banner)

    # testing the PrepareBan function
    ban_enum = await bot.PrepareBan(TargetId=banne_id, Sender=banner_member)
    assert ban_enum == BanLookup.Banned

    db_ban_entry = bot.Database.Database.execute(f"SELECT * FROM banslist WHERE Id={banne_id}").fetchone()
    assert db_ban_entry[0] == banne_id
    assert db_ban_entry[1] == banner_name
    assert db_ban_entry[2] == banner_id
    # date isn't tested since I found there was milliseconds of difference
    
    dup_ban_enum = await bot.PrepareBan(TargetId=12345, Sender=banner_member)
    assert dup_ban_enum == BanLookup.Duplicate

