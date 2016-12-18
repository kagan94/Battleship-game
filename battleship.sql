/*
Navicat MySQL Data Transfer

Source Server         : 1
Source Server Version : 50626
Source Host           : 127.0.0.1:3306
Source Database       : battleship

Target Server Type    : MYSQL
Target Server Version : 50626
File Encoding         : 65001

Date: 2016-12-18 16:33:18
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for map
-- ----------------------------
DROP TABLE IF EXISTS `map`;
CREATE TABLE `map` (
  `map_id` int(11) NOT NULL AUTO_INCREMENT,
  `server_id` int(11) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `owner_id` int(11) DEFAULT NULL,
  `size` int(6) DEFAULT NULL COMMENT 'number of rows on this field',
  `max_players` int(11) DEFAULT '0' COMMENT 'Maximum number of players',
  `game_started` int(1) DEFAULT '0' COMMENT '0 - not started yet, 1 - game started, 2 game finished',
  PRIMARY KEY (`map_id`),
  KEY `map_ibfk_1` (`server_id`),
  KEY `owner_id` (`owner_id`),
  CONSTRAINT `map_ibfk_1` FOREIGN KEY (`server_id`) REFERENCES `server` (`server_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `map_ibfk_2` FOREIGN KEY (`owner_id`) REFERENCES `player` (`player_id`)
) ENGINE=InnoDB AUTO_INCREMENT=111 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of map
-- ----------------------------
INSERT INTO `map` VALUES ('99', '2', 'dasd sad a', '48', '20', '3', '0');
INSERT INTO `map` VALUES ('100', '2', 'test map', '45', '20', '3', '1');
INSERT INTO `map` VALUES ('103', '2', 'my map', '45', '40', '13', '2');
INSERT INTO `map` VALUES ('104', '2', '3123', '46', '20', '3', '1');
INSERT INTO `map` VALUES ('106', '2', 'dasdas', '45', '20', '3', '0');
INSERT INTO `map` VALUES ('107', '2', '777', '46', '20', '3', '0');
INSERT INTO `map` VALUES ('108', '2', '8', '50', '20', '3', '0');
INSERT INTO `map` VALUES ('109', '2', '88', '50', '20', '3', '0');
INSERT INTO `map` VALUES ('110', '2', 'My_map', '49', '20', '3', '1');

-- ----------------------------
-- Table structure for player
-- ----------------------------
DROP TABLE IF EXISTS `player`;
CREATE TABLE `player` (
  `player_id` int(11) NOT NULL AUTO_INCREMENT,
  `nickname` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of player
-- ----------------------------
INSERT INTO `player` VALUES ('45', 'rrr');
INSERT INTO `player` VALUES ('46', 'sss');
INSERT INTO `player` VALUES ('47', 'dassad');
INSERT INTO `player` VALUES ('48', '123sa');
INSERT INTO `player` VALUES ('49', 'ff');
INSERT INTO `player` VALUES ('50', 'dasdas');
INSERT INTO `player` VALUES ('51', 'dsad');
INSERT INTO `player` VALUES ('52', 'My_nickname');

-- ----------------------------
-- Table structure for player_hits
-- ----------------------------
DROP TABLE IF EXISTS `player_hits`;
CREATE TABLE `player_hits` (
  `shot_id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) DEFAULT NULL,
  `player_id` int(11) DEFAULT NULL,
  `row` int(11) DEFAULT NULL,
  `column` int(11) DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  `hit` int(11) DEFAULT '0' COMMENT 'If shot hit in someone = 1, otherwise 0',
  `ship_location_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`shot_id`),
  KEY `player_hits_ibfk_1` (`map_id`),
  KEY `player_hits_ibfk_2` (`player_id`),
  CONSTRAINT `player_hits_ibfk_1` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1246 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of player_hits
-- ----------------------------
INSERT INTO `player_hits` VALUES ('699', '100', '45', '2', '6', '2016-12-16 20:42:07', '0', null);
INSERT INTO `player_hits` VALUES ('700', '100', '46', '2', '8', '2016-12-16 20:42:26', '0', null);
INSERT INTO `player_hits` VALUES ('701', '100', '45', '3', '9', '2016-12-16 20:42:38', '0', null);
INSERT INTO `player_hits` VALUES ('702', '100', '46', '12', '4', '2016-12-16 20:42:43', '0', null);
INSERT INTO `player_hits` VALUES ('703', '100', '45', '1', '6', '2016-12-16 20:42:51', '0', null);
INSERT INTO `player_hits` VALUES ('704', '100', '46', '2', '12', '2016-12-16 20:43:03', '0', null);
INSERT INTO `player_hits` VALUES ('705', '100', '45', '0', '8', '2016-12-16 20:43:07', '1', null);
INSERT INTO `player_hits` VALUES ('706', '100', '45', '0', '8', '2016-12-16 20:43:07', '1', null);
INSERT INTO `player_hits` VALUES ('707', '100', '45', '7', '7', '2016-12-16 20:54:34', '0', null);
INSERT INTO `player_hits` VALUES ('708', '100', '46', '5', '10', '2016-12-16 20:54:39', '0', null);
INSERT INTO `player_hits` VALUES ('709', '100', '45', '3', '5', '2016-12-16 20:54:52', '0', null);
INSERT INTO `player_hits` VALUES ('710', '100', '46', '4', '4', '2016-12-16 20:55:03', '1', null);
INSERT INTO `player_hits` VALUES ('711', '100', '46', '4', '4', '2016-12-16 20:55:03', '1', null);
INSERT INTO `player_hits` VALUES ('712', '100', '45', '12', '5', '2016-12-16 20:58:51', '0', null);
INSERT INTO `player_hits` VALUES ('713', '100', '45', '10', '8', '2016-12-16 21:19:38', '0', null);
INSERT INTO `player_hits` VALUES ('714', '100', '45', '6', '3', '2016-12-16 21:20:59', '0', null);
INSERT INTO `player_hits` VALUES ('715', '100', '46', '8', '6', '2016-12-16 21:21:04', '0', null);
INSERT INTO `player_hits` VALUES ('716', '100', '45', '5', '1', '2016-12-16 21:21:17', '0', null);
INSERT INTO `player_hits` VALUES ('717', '100', '46', '10', '14', '2016-12-16 21:21:23', '1', null);
INSERT INTO `player_hits` VALUES ('718', '100', '46', '10', '14', '2016-12-16 21:21:23', '1', '858');
INSERT INTO `player_hits` VALUES ('719', '100', '45', '12', '7', '2016-12-16 21:32:22', '0', null);
INSERT INTO `player_hits` VALUES ('720', '100', '45', '11', '9', '2016-12-16 21:32:55', '1', null);
INSERT INTO `player_hits` VALUES ('721', '100', '45', '11', '9', '2016-12-16 21:32:55', '1', '849');
INSERT INTO `player_hits` VALUES ('722', '100', '45', '11', '10', '2016-12-16 21:32:58', '0', null);
INSERT INTO `player_hits` VALUES ('723', '100', '45', '13', '10', '2016-12-16 21:34:20', '0', null);
INSERT INTO `player_hits` VALUES ('724', '100', '45', '13', '11', '2016-12-16 21:34:44', '0', null);
INSERT INTO `player_hits` VALUES ('725', '100', '46', '9', '14', '2016-12-16 21:35:55', '0', null);
INSERT INTO `player_hits` VALUES ('726', '100', '45', '8', '14', '2016-12-16 21:35:57', '0', null);
INSERT INTO `player_hits` VALUES ('727', '100', '46', '11', '14', '2016-12-16 21:36:01', '1', null);
INSERT INTO `player_hits` VALUES ('728', '100', '46', '11', '14', '2016-12-16 21:36:01', '1', '858');
INSERT INTO `player_hits` VALUES ('729', '100', '46', '12', '14', '2016-12-16 21:36:03', '1', null);
INSERT INTO `player_hits` VALUES ('730', '100', '46', '12', '14', '2016-12-16 21:36:03', '1', '858');
INSERT INTO `player_hits` VALUES ('731', '100', '46', '13', '14', '2016-12-16 21:36:05', '1', null);
INSERT INTO `player_hits` VALUES ('732', '100', '46', '13', '14', '2016-12-16 21:36:05', '1', '858');
INSERT INTO `player_hits` VALUES ('733', '100', '46', '14', '12', '2016-12-16 21:36:15', '0', null);
INSERT INTO `player_hits` VALUES ('734', '100', '45', '14', '14', '2016-12-16 21:36:20', '0', null);
INSERT INTO `player_hits` VALUES ('735', '100', '46', '17', '0', '2016-12-16 21:36:21', '0', null);
INSERT INTO `player_hits` VALUES ('736', '100', '45', '18', '0', '2016-12-16 21:36:30', '0', null);
INSERT INTO `player_hits` VALUES ('737', '100', '46', '5', '4', '2016-12-16 21:36:38', '1', null);
INSERT INTO `player_hits` VALUES ('738', '100', '46', '5', '4', '2016-12-16 21:36:38', '1', '861');
INSERT INTO `player_hits` VALUES ('739', '100', '46', '7', '4', '2016-12-16 21:36:56', '0', null);
INSERT INTO `player_hits` VALUES ('740', '100', '45', '9', '3', '2016-12-16 21:37:04', '0', null);
INSERT INTO `player_hits` VALUES ('741', '100', '46', '8', '3', '2016-12-16 21:37:08', '1', null);
INSERT INTO `player_hits` VALUES ('742', '100', '46', '8', '3', '2016-12-16 21:37:08', '1', '865');
INSERT INTO `player_hits` VALUES ('743', '100', '46', '14', '3', '2016-12-16 21:37:31', '0', null);
INSERT INTO `player_hits` VALUES ('744', '100', '45', '12', '3', '2016-12-16 21:37:37', '1', null);
INSERT INTO `player_hits` VALUES ('745', '100', '45', '12', '3', '2016-12-16 21:37:37', '1', '854');
INSERT INTO `player_hits` VALUES ('746', '100', '45', '12', '0', '2016-12-16 21:37:38', '1', null);
INSERT INTO `player_hits` VALUES ('747', '100', '45', '12', '0', '2016-12-16 21:37:38', '1', '857');
INSERT INTO `player_hits` VALUES ('748', '100', '45', '12', '6', '2016-12-16 21:37:41', '1', null);
INSERT INTO `player_hits` VALUES ('749', '100', '45', '12', '6', '2016-12-16 21:37:41', '1', '856');
INSERT INTO `player_hits` VALUES ('750', '100', '45', '12', '9', '2016-12-16 21:37:42', '1', null);
INSERT INTO `player_hits` VALUES ('751', '100', '45', '12', '9', '2016-12-16 21:37:42', '1', '849');
INSERT INTO `player_hits` VALUES ('752', '100', '45', '13', '9', '2016-12-16 21:37:43', '1', null);
INSERT INTO `player_hits` VALUES ('753', '100', '45', '13', '9', '2016-12-16 21:37:43', '1', '849');
INSERT INTO `player_hits` VALUES ('754', '100', '45', '12', '12', '2016-12-16 21:37:46', '1', null);
INSERT INTO `player_hits` VALUES ('755', '100', '45', '12', '12', '2016-12-16 21:37:46', '1', '851');
INSERT INTO `player_hits` VALUES ('756', '100', '45', '13', '12', '2016-12-16 21:37:47', '1', null);
INSERT INTO `player_hits` VALUES ('757', '100', '45', '13', '12', '2016-12-16 21:37:47', '1', '851');
INSERT INTO `player_hits` VALUES ('758', '100', '45', '11', '16', '2016-12-16 21:37:52', '1', null);
INSERT INTO `player_hits` VALUES ('759', '100', '45', '11', '16', '2016-12-16 21:37:52', '1', '853');
INSERT INTO `player_hits` VALUES ('760', '100', '45', '12', '16', '2016-12-16 21:37:52', '1', null);
INSERT INTO `player_hits` VALUES ('761', '100', '45', '12', '16', '2016-12-16 21:37:52', '1', '853');
INSERT INTO `player_hits` VALUES ('762', '100', '45', '13', '19', '2016-12-16 21:37:54', '1', null);
INSERT INTO `player_hits` VALUES ('763', '100', '45', '13', '19', '2016-12-16 21:37:54', '1', '852');
INSERT INTO `player_hits` VALUES ('764', '100', '45', '14', '19', '2016-12-16 21:37:55', '1', null);
INSERT INTO `player_hits` VALUES ('765', '100', '45', '14', '19', '2016-12-16 21:37:55', '1', '852');
INSERT INTO `player_hits` VALUES ('766', '100', '45', '0', '6', '2016-12-16 21:38:11', '1', null);
INSERT INTO `player_hits` VALUES ('767', '100', '45', '0', '6', '2016-12-16 21:38:11', '1', '850');
INSERT INTO `player_hits` VALUES ('768', '100', '45', '0', '7', '2016-12-16 21:38:12', '1', null);
INSERT INTO `player_hits` VALUES ('769', '100', '45', '0', '7', '2016-12-16 21:38:12', '1', '850');
INSERT INTO `player_hits` VALUES ('770', '100', '45', '4', '17', '2016-12-16 21:38:19', '1', null);
INSERT INTO `player_hits` VALUES ('771', '100', '45', '4', '17', '2016-12-16 21:38:19', '1', '855');
INSERT INTO `player_hits` VALUES ('772', '100', '45', '18', '10', '2016-12-16 21:38:24', '1', null);
INSERT INTO `player_hits` VALUES ('773', '100', '45', '18', '10', '2016-12-16 21:38:24', '1', '848');
INSERT INTO `player_hits` VALUES ('774', '100', '45', '18', '11', '2016-12-16 21:38:25', '1', null);
INSERT INTO `player_hits` VALUES ('775', '100', '45', '18', '11', '2016-12-16 21:38:25', '1', '848');
INSERT INTO `player_hits` VALUES ('776', '100', '45', '18', '12', '2016-12-16 21:38:27', '1', null);
INSERT INTO `player_hits` VALUES ('777', '100', '45', '18', '12', '2016-12-16 21:38:27', '1', '848');
INSERT INTO `player_hits` VALUES ('778', '100', '45', '18', '13', '2016-12-16 21:38:28', '1', null);
INSERT INTO `player_hits` VALUES ('779', '100', '45', '18', '13', '2016-12-16 21:38:28', '1', '848');
INSERT INTO `player_hits` VALUES ('780', '100', '45', '5', '19', '2016-12-16 21:47:25', '0', null);
INSERT INTO `player_hits` VALUES ('781', '100', '46', '1', '2', '2016-12-16 21:59:15', '0', null);
INSERT INTO `player_hits` VALUES ('782', '100', '45', '1', '1', '2016-12-16 21:59:24', '0', null);
INSERT INTO `player_hits` VALUES ('783', '100', '46', '3', '12', '2016-12-16 21:59:29', '0', null);
INSERT INTO `player_hits` VALUES ('784', '100', '45', '9', '8', '2016-12-16 21:59:51', '0', null);
INSERT INTO `player_hits` VALUES ('845', '103', '45', '7', '17', '2016-12-17 21:27:49', '0', null);
INSERT INTO `player_hits` VALUES ('847', '103', '45', '22', '12', '2016-12-17 21:27:59', '0', null);
INSERT INTO `player_hits` VALUES ('861', '103', '45', '25', '24', '2016-12-17 21:28:28', '0', null);
INSERT INTO `player_hits` VALUES ('867', '103', '45', '33', '36', '2016-12-17 21:29:14', '0', null);
INSERT INTO `player_hits` VALUES ('873', '103', '45', '28', '26', '2016-12-17 21:29:24', '0', null);
INSERT INTO `player_hits` VALUES ('879', '103', '45', '34', '12', '2016-12-17 21:29:55', '0', null);
INSERT INTO `player_hits` VALUES ('895', '103', '45', '27', '11', '2016-12-17 21:30:13', '0', null);
INSERT INTO `player_hits` VALUES ('898', '104', '46', '4', '7', '2016-12-17 23:36:04', '0', null);
INSERT INTO `player_hits` VALUES ('899', '104', '45', '3', '9', '2016-12-17 23:36:10', '0', null);
INSERT INTO `player_hits` VALUES ('900', '104', '46', '3', '11', '2016-12-17 23:36:14', '0', null);
INSERT INTO `player_hits` VALUES ('901', '104', '45', '2', '10', '2016-12-17 23:36:16', '1', null);
INSERT INTO `player_hits` VALUES ('902', '104', '45', '2', '10', '2016-12-17 23:36:16', '1', '918');
INSERT INTO `player_hits` VALUES ('903', '104', '45', '3', '10', '2016-12-17 23:36:17', '1', null);
INSERT INTO `player_hits` VALUES ('904', '104', '45', '3', '10', '2016-12-17 23:36:17', '1', '918');
INSERT INTO `player_hits` VALUES ('905', '104', '45', '1', '10', '2016-12-17 23:36:18', '1', null);
INSERT INTO `player_hits` VALUES ('906', '104', '45', '1', '10', '2016-12-17 23:36:18', '1', '918');
INSERT INTO `player_hits` VALUES ('907', '104', '45', '0', '10', '2016-12-17 23:36:18', '1', null);
INSERT INTO `player_hits` VALUES ('908', '104', '45', '0', '10', '2016-12-17 23:36:18', '1', '918');
INSERT INTO `player_hits` VALUES ('909', '104', '45', '4', '10', '2016-12-17 23:36:20', '0', null);
INSERT INTO `player_hits` VALUES ('910', '104', '46', '10', '7', '2016-12-17 23:36:42', '0', null);
INSERT INTO `player_hits` VALUES ('911', '104', '45', '14', '10', '2016-12-17 23:37:04', '1', null);
INSERT INTO `player_hits` VALUES ('912', '104', '45', '14', '10', '2016-12-17 23:37:04', '1', '919');
INSERT INTO `player_hits` VALUES ('913', '104', '45', '13', '10', '2016-12-17 23:37:05', '0', null);
INSERT INTO `player_hits` VALUES ('1217', '110', '49', '5', '10', '2016-12-18 16:22:09', '0', null);
INSERT INTO `player_hits` VALUES ('1218', '110', '46', '3', '11', '2016-12-18 16:22:12', '1', null);
INSERT INTO `player_hits` VALUES ('1219', '110', '46', '3', '11', '2016-12-18 16:22:12', '1', '1100');
INSERT INTO `player_hits` VALUES ('1220', '110', '46', '4', '14', '2016-12-18 16:26:25', '0', null);
INSERT INTO `player_hits` VALUES ('1221', '110', '52', '2', '13', '2016-12-18 16:26:32', '0', null);
INSERT INTO `player_hits` VALUES ('1222', '110', '49', '3', '8', '2016-12-18 16:26:37', '0', null);
INSERT INTO `player_hits` VALUES ('1223', '110', '46', '3', '12', '2016-12-18 16:26:40', '1', null);
INSERT INTO `player_hits` VALUES ('1224', '110', '46', '3', '12', '2016-12-18 16:26:40', '1', '1100');
INSERT INTO `player_hits` VALUES ('1225', '110', '46', '3', '13', '2016-12-18 16:26:41', '1', null);
INSERT INTO `player_hits` VALUES ('1226', '110', '46', '3', '13', '2016-12-18 16:26:41', '1', '1100');
INSERT INTO `player_hits` VALUES ('1227', '110', '46', '2', '9', '2016-12-18 16:26:47', '1', null);
INSERT INTO `player_hits` VALUES ('1228', '110', '46', '2', '9', '2016-12-18 16:26:47', '1', '1106');
INSERT INTO `player_hits` VALUES ('1229', '110', '46', '0', '10', '2016-12-18 16:26:50', '1', null);
INSERT INTO `player_hits` VALUES ('1230', '110', '46', '0', '10', '2016-12-18 16:26:50', '1', '1104');
INSERT INTO `player_hits` VALUES ('1231', '110', '46', '0', '8', '2016-12-18 16:26:56', '1', null);
INSERT INTO `player_hits` VALUES ('1232', '110', '46', '0', '8', '2016-12-18 16:26:56', '1', '1083');
INSERT INTO `player_hits` VALUES ('1233', '110', '46', '0', '7', '2016-12-18 16:26:56', '1', null);
INSERT INTO `player_hits` VALUES ('1234', '110', '46', '0', '7', '2016-12-18 16:26:56', '1', '1083');
INSERT INTO `player_hits` VALUES ('1235', '110', '46', '19', '3', '2016-12-18 16:27:02', '0', null);
INSERT INTO `player_hits` VALUES ('1236', '110', '52', '18', '4', '2016-12-18 16:27:06', '0', null);
INSERT INTO `player_hits` VALUES ('1237', '110', '49', '19', '6', '2016-12-18 16:27:15', '1', null);
INSERT INTO `player_hits` VALUES ('1238', '110', '49', '19', '6', '2016-12-18 16:27:15', '1', '1103');
INSERT INTO `player_hits` VALUES ('1239', '110', '49', '7', '12', '2016-12-18 16:28:14', '1', null);
INSERT INTO `player_hits` VALUES ('1240', '110', '49', '7', '12', '2016-12-18 16:28:14', '1', '1089');
INSERT INTO `player_hits` VALUES ('1241', '110', '49', '8', '12', '2016-12-18 16:28:16', '1', null);
INSERT INTO `player_hits` VALUES ('1242', '110', '49', '8', '12', '2016-12-18 16:28:16', '1', '1089');
INSERT INTO `player_hits` VALUES ('1243', '110', '49', '9', '12', '2016-12-18 16:28:16', '1', null);
INSERT INTO `player_hits` VALUES ('1244', '110', '49', '9', '12', '2016-12-18 16:28:16', '1', '1089');
INSERT INTO `player_hits` VALUES ('1245', '110', '49', '10', '12', '2016-12-18 16:28:26', '0', null);

-- ----------------------------
-- Table structure for player_to_map
-- ----------------------------
DROP TABLE IF EXISTS `player_to_map`;
CREATE TABLE `player_to_map` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) NOT NULL,
  `player_id` int(11) NOT NULL,
  `time_connected` datetime DEFAULT NULL,
  `disconnected` int(1) NOT NULL DEFAULT '0' COMMENT '0 - no, 1 - yes',
  `my_turn` int(1) DEFAULT '0' COMMENT '0 - no, 1 yes',
  `kicked` int(1) NOT NULL DEFAULT '0' COMMENT '0 - no, 1 - yes',
  `spectator_mode` int(1) NOT NULL DEFAULT '0' COMMENT '0 - no, 1 - yes',
  `turn_start_time` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `player_to_map_ibfk_1` (`map_id`),
  KEY `player_to_map_ibfk_2` (`player_id`),
  CONSTRAINT `player_to_map_ibfk_1` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `player_to_map_ibfk_2` FOREIGN KEY (`player_id`) REFERENCES `player` (`player_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of player_to_map
-- ----------------------------
INSERT INTO `player_to_map` VALUES ('16', '99', '45', '2016-12-16 20:36:00', '1', '0', '0', '0', '0000-00-00 00:00:00');
INSERT INTO `player_to_map` VALUES ('17', '99', '46', '2016-12-16 20:36:53', '1', '0', '1', '0', '0000-00-00 00:00:00');
INSERT INTO `player_to_map` VALUES ('18', '100', '45', '2016-12-16 20:37:58', '0', '0', '1', '0', '0000-00-00 00:00:00');
INSERT INTO `player_to_map` VALUES ('24', '103', '45', '2016-12-17 21:26:16', '0', '0', '0', '0', '0000-00-00 00:00:00');
INSERT INTO `player_to_map` VALUES ('26', '104', '46', '2016-12-17 21:45:03', '0', '1', '0', '0', '0000-00-00 00:00:00');
INSERT INTO `player_to_map` VALUES ('27', '104', '45', '2016-12-17 23:35:46', '1', '0', '0', '0', '0000-00-00 00:00:00');
INSERT INTO `player_to_map` VALUES ('30', '106', '45', '2016-12-18 01:10:27', '0', '1', '0', '0', '0000-00-00 00:00:00');
INSERT INTO `player_to_map` VALUES ('32', '107', '45', '2016-12-18 01:12:42', '1', '1', '0', '0', '0000-00-00 00:00:00');
INSERT INTO `player_to_map` VALUES ('35', '109', '52', '2016-12-18 16:00:50', '0', '0', '0', '0', '2016-12-18 16:00:50');
INSERT INTO `player_to_map` VALUES ('36', '110', '49', '2016-12-18 16:15:20', '0', '0', '0', '0', '2016-12-18 16:15:20');
INSERT INTO `player_to_map` VALUES ('37', '110', '46', '2016-12-18 16:15:54', '0', '1', '0', '0', '2016-12-18 16:15:54');
INSERT INTO `player_to_map` VALUES ('38', '110', '52', '2016-12-18 16:16:24', '0', '0', '0', '0', '2016-12-18 16:16:24');

-- ----------------------------
-- Table structure for server
-- ----------------------------
DROP TABLE IF EXISTS `server`;
CREATE TABLE `server` (
  `server_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`server_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of server
-- ----------------------------
INSERT INTO `server` VALUES ('1', 'server1');
INSERT INTO `server` VALUES ('2', 'server2');
INSERT INTO `server` VALUES ('3', '123');
INSERT INTO `server` VALUES ('4', 'Best server ever');
INSERT INTO `server` VALUES ('5', 'Tartu server');

-- ----------------------------
-- Table structure for ship_to_map
-- ----------------------------
DROP TABLE IF EXISTS `ship_to_map`;
CREATE TABLE `ship_to_map` (
  `location_id` int(11) NOT NULL AUTO_INCREMENT,
  `map_id` int(11) NOT NULL,
  `player_id` int(11) NOT NULL,
  `row_start` int(5) DEFAULT NULL,
  `row_end` int(5) DEFAULT NULL,
  `column_start` int(5) DEFAULT NULL,
  `column_end` int(5) DEFAULT NULL,
  `ship_type` int(1) NOT NULL DEFAULT '1' COMMENT 'size of ship (''1'',''2'',''3'',''4'')',
  `totally_sank` int(1) DEFAULT '0' COMMENT '0 - no, 1 - yes',
  PRIMARY KEY (`location_id`),
  KEY `ship_to_map_ibfk_3` (`player_id`),
  KEY `ship_to_map_ibfk_4` (`map_id`),
  CONSTRAINT `ship_to_map_ibfk_3` FOREIGN KEY (`player_id`) REFERENCES `player` (`player_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ship_to_map_ibfk_4` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1108 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of ship_to_map
-- ----------------------------
INSERT INTO `ship_to_map` VALUES ('848', '100', '46', '18', '18', '10', '13', '4', '1');
INSERT INTO `ship_to_map` VALUES ('849', '100', '46', '11', '13', '9', '9', '3', '1');
INSERT INTO `ship_to_map` VALUES ('850', '100', '46', '0', '0', '6', '8', '3', '0');
INSERT INTO `ship_to_map` VALUES ('851', '100', '46', '12', '13', '12', '12', '2', '1');
INSERT INTO `ship_to_map` VALUES ('852', '100', '46', '13', '14', '19', '19', '2', '1');
INSERT INTO `ship_to_map` VALUES ('853', '100', '46', '11', '12', '16', '16', '2', '1');
INSERT INTO `ship_to_map` VALUES ('854', '100', '46', '12', '12', '3', '3', '1', '1');
INSERT INTO `ship_to_map` VALUES ('855', '100', '46', '4', '4', '17', '17', '1', '1');
INSERT INTO `ship_to_map` VALUES ('856', '100', '46', '12', '12', '6', '6', '1', '1');
INSERT INTO `ship_to_map` VALUES ('857', '100', '46', '12', '12', '0', '0', '1', '1');
INSERT INTO `ship_to_map` VALUES ('858', '100', '45', '10', '13', '14', '14', '4', '1');
INSERT INTO `ship_to_map` VALUES ('859', '100', '45', '3', '5', '15', '15', '3', '0');
INSERT INTO `ship_to_map` VALUES ('860', '100', '45', '4', '4', '11', '13', '3', '0');
INSERT INTO `ship_to_map` VALUES ('861', '100', '45', '4', '5', '4', '4', '2', '0');
INSERT INTO `ship_to_map` VALUES ('862', '100', '45', '17', '17', '7', '8', '2', '0');
INSERT INTO `ship_to_map` VALUES ('863', '100', '45', '17', '18', '16', '16', '2', '0');
INSERT INTO `ship_to_map` VALUES ('864', '100', '45', '18', '18', '18', '18', '1', '0');
INSERT INTO `ship_to_map` VALUES ('865', '100', '45', '8', '8', '3', '3', '1', '1');
INSERT INTO `ship_to_map` VALUES ('866', '100', '45', '15', '15', '8', '8', '1', '0');
INSERT INTO `ship_to_map` VALUES ('867', '100', '45', '11', '11', '18', '18', '1', '0');
INSERT INTO `ship_to_map` VALUES ('868', '99', '45', '4', '7', '15', '15', '4', '0');
INSERT INTO `ship_to_map` VALUES ('869', '99', '45', '9', '9', '2', '4', '3', '0');
INSERT INTO `ship_to_map` VALUES ('870', '99', '45', '12', '14', '9', '9', '3', '0');
INSERT INTO `ship_to_map` VALUES ('871', '99', '45', '9', '9', '15', '16', '2', '0');
INSERT INTO `ship_to_map` VALUES ('872', '99', '45', '17', '17', '15', '16', '2', '0');
INSERT INTO `ship_to_map` VALUES ('873', '99', '45', '15', '16', '19', '19', '2', '0');
INSERT INTO `ship_to_map` VALUES ('874', '99', '45', '14', '14', '17', '17', '1', '0');
INSERT INTO `ship_to_map` VALUES ('875', '99', '45', '10', '10', '7', '7', '1', '0');
INSERT INTO `ship_to_map` VALUES ('876', '99', '45', '14', '14', '1', '1', '1', '0');
INSERT INTO `ship_to_map` VALUES ('877', '99', '45', '16', '16', '0', '0', '1', '0');
INSERT INTO `ship_to_map` VALUES ('898', '103', '45', '27', '30', '16', '16', '4', '1');
INSERT INTO `ship_to_map` VALUES ('899', '103', '45', '13', '15', '17', '17', '3', '1');
INSERT INTO `ship_to_map` VALUES ('900', '103', '45', '34', '34', '9', '11', '3', '1');
INSERT INTO `ship_to_map` VALUES ('901', '103', '45', '34', '35', '36', '36', '2', '1');
INSERT INTO `ship_to_map` VALUES ('902', '103', '45', '20', '21', '12', '12', '2', '1');
INSERT INTO `ship_to_map` VALUES ('903', '103', '45', '10', '11', '27', '27', '2', '1');
INSERT INTO `ship_to_map` VALUES ('904', '103', '45', '29', '29', '26', '26', '1', '1');
INSERT INTO `ship_to_map` VALUES ('905', '103', '45', '28', '28', '11', '11', '1', '1');
INSERT INTO `ship_to_map` VALUES ('906', '103', '45', '24', '24', '38', '38', '1', '1');
INSERT INTO `ship_to_map` VALUES ('907', '103', '45', '16', '16', '12', '12', '1', '1');
INSERT INTO `ship_to_map` VALUES ('918', '104', '46', '0', '3', '10', '10', '4', '1');
INSERT INTO `ship_to_map` VALUES ('919', '104', '46', '14', '14', '8', '10', '3', '0');
INSERT INTO `ship_to_map` VALUES ('920', '104', '46', '5', '7', '18', '18', '3', '0');
INSERT INTO `ship_to_map` VALUES ('921', '104', '46', '12', '13', '1', '1', '2', '0');
INSERT INTO `ship_to_map` VALUES ('922', '104', '46', '1', '2', '0', '0', '2', '0');
INSERT INTO `ship_to_map` VALUES ('923', '104', '46', '7', '8', '15', '15', '2', '0');
INSERT INTO `ship_to_map` VALUES ('924', '104', '46', '0', '0', '15', '15', '1', '0');
INSERT INTO `ship_to_map` VALUES ('925', '104', '46', '17', '17', '12', '12', '1', '0');
INSERT INTO `ship_to_map` VALUES ('926', '104', '46', '13', '13', '16', '16', '1', '0');
INSERT INTO `ship_to_map` VALUES ('927', '104', '46', '5', '5', '16', '16', '1', '0');
INSERT INTO `ship_to_map` VALUES ('928', '104', '45', '2', '2', '12', '15', '4', '0');
INSERT INTO `ship_to_map` VALUES ('929', '104', '45', '11', '13', '5', '5', '3', '0');
INSERT INTO `ship_to_map` VALUES ('930', '104', '45', '3', '3', '17', '19', '3', '0');
INSERT INTO `ship_to_map` VALUES ('931', '104', '45', '17', '17', '1', '2', '2', '0');
INSERT INTO `ship_to_map` VALUES ('932', '104', '45', '12', '13', '3', '3', '2', '0');
INSERT INTO `ship_to_map` VALUES ('933', '104', '45', '10', '10', '13', '14', '2', '0');
INSERT INTO `ship_to_map` VALUES ('934', '104', '45', '7', '7', '1', '1', '1', '0');
INSERT INTO `ship_to_map` VALUES ('935', '104', '45', '19', '19', '11', '11', '1', '0');
INSERT INTO `ship_to_map` VALUES ('936', '104', '45', '4', '4', '2', '2', '1', '0');
INSERT INTO `ship_to_map` VALUES ('937', '104', '45', '4', '4', '0', '0', '1', '0');
INSERT INTO `ship_to_map` VALUES ('968', '106', '45', '12', '12', '2', '5', '4', '0');
INSERT INTO `ship_to_map` VALUES ('969', '106', '45', '18', '18', '2', '4', '3', '0');
INSERT INTO `ship_to_map` VALUES ('970', '106', '45', '2', '4', '4', '4', '3', '0');
INSERT INTO `ship_to_map` VALUES ('971', '106', '45', '5', '6', '13', '13', '2', '0');
INSERT INTO `ship_to_map` VALUES ('972', '106', '45', '15', '15', '0', '1', '2', '0');
INSERT INTO `ship_to_map` VALUES ('973', '106', '45', '13', '13', '11', '12', '2', '0');
INSERT INTO `ship_to_map` VALUES ('974', '106', '45', '7', '7', '6', '6', '1', '0');
INSERT INTO `ship_to_map` VALUES ('975', '106', '45', '17', '17', '16', '16', '1', '0');
INSERT INTO `ship_to_map` VALUES ('976', '106', '45', '18', '18', '0', '0', '1', '0');
INSERT INTO `ship_to_map` VALUES ('977', '106', '45', '8', '8', '0', '0', '1', '0');
INSERT INTO `ship_to_map` VALUES ('1068', '109', '52', '12', '12', '7', '10', '4', '0');
INSERT INTO `ship_to_map` VALUES ('1069', '109', '52', '11', '13', '16', '16', '3', '0');
INSERT INTO `ship_to_map` VALUES ('1070', '109', '52', '15', '15', '16', '18', '3', '0');
INSERT INTO `ship_to_map` VALUES ('1071', '109', '52', '2', '2', '0', '1', '2', '0');
INSERT INTO `ship_to_map` VALUES ('1072', '109', '52', '3', '4', '18', '18', '2', '0');
INSERT INTO `ship_to_map` VALUES ('1073', '109', '52', '16', '16', '11', '12', '2', '0');
INSERT INTO `ship_to_map` VALUES ('1074', '109', '52', '19', '19', '14', '14', '1', '0');
INSERT INTO `ship_to_map` VALUES ('1075', '109', '52', '12', '12', '3', '3', '1', '0');
INSERT INTO `ship_to_map` VALUES ('1076', '109', '52', '15', '15', '6', '6', '1', '0');
INSERT INTO `ship_to_map` VALUES ('1077', '109', '52', '19', '19', '19', '19', '1', '0');
INSERT INTO `ship_to_map` VALUES ('1078', '110', '49', '13', '13', '2', '5', '4', '0');
INSERT INTO `ship_to_map` VALUES ('1079', '110', '49', '2', '4', '3', '3', '3', '0');
INSERT INTO `ship_to_map` VALUES ('1080', '110', '49', '14', '16', '8', '8', '3', '0');
INSERT INTO `ship_to_map` VALUES ('1081', '110', '49', '13', '14', '13', '13', '2', '0');
INSERT INTO `ship_to_map` VALUES ('1082', '110', '49', '2', '3', '5', '5', '2', '0');
INSERT INTO `ship_to_map` VALUES ('1083', '110', '49', '0', '0', '7', '8', '2', '1');
INSERT INTO `ship_to_map` VALUES ('1084', '110', '49', '8', '8', '2', '2', '1', '0');
INSERT INTO `ship_to_map` VALUES ('1085', '110', '49', '7', '7', '6', '6', '1', '0');
INSERT INTO `ship_to_map` VALUES ('1086', '110', '49', '13', '13', '10', '10', '1', '0');
INSERT INTO `ship_to_map` VALUES ('1087', '110', '49', '17', '17', '10', '10', '1', '0');
INSERT INTO `ship_to_map` VALUES ('1088', '110', '46', '11', '14', '16', '16', '4', '0');
INSERT INTO `ship_to_map` VALUES ('1089', '110', '46', '7', '9', '12', '12', '3', '1');
INSERT INTO `ship_to_map` VALUES ('1090', '110', '46', '17', '17', '16', '18', '3', '0');
INSERT INTO `ship_to_map` VALUES ('1091', '110', '46', '10', '11', '19', '19', '2', '0');
INSERT INTO `ship_to_map` VALUES ('1092', '110', '46', '5', '5', '18', '19', '2', '0');
INSERT INTO `ship_to_map` VALUES ('1093', '110', '46', '14', '15', '0', '0', '2', '0');
INSERT INTO `ship_to_map` VALUES ('1094', '110', '46', '7', '7', '14', '14', '1', '0');
INSERT INTO `ship_to_map` VALUES ('1095', '110', '46', '14', '14', '18', '18', '1', '0');
INSERT INTO `ship_to_map` VALUES ('1096', '110', '46', '6', '6', '10', '10', '1', '0');
INSERT INTO `ship_to_map` VALUES ('1097', '110', '46', '7', '7', '4', '4', '1', '0');
INSERT INTO `ship_to_map` VALUES ('1098', '110', '52', '6', '9', '0', '0', '4', '0');
INSERT INTO `ship_to_map` VALUES ('1099', '110', '52', '11', '11', '8', '10', '3', '0');
INSERT INTO `ship_to_map` VALUES ('1100', '110', '52', '3', '3', '11', '13', '3', '1');
INSERT INTO `ship_to_map` VALUES ('1101', '110', '52', '10', '10', '4', '5', '2', '0');
INSERT INTO `ship_to_map` VALUES ('1102', '110', '52', '7', '7', '18', '19', '2', '0');
INSERT INTO `ship_to_map` VALUES ('1103', '110', '52', '18', '19', '6', '6', '2', '0');
INSERT INTO `ship_to_map` VALUES ('1104', '110', '52', '0', '0', '10', '10', '1', '1');
INSERT INTO `ship_to_map` VALUES ('1105', '110', '52', '1', '1', '17', '17', '1', '0');
INSERT INTO `ship_to_map` VALUES ('1106', '110', '52', '2', '2', '9', '9', '1', '1');
INSERT INTO `ship_to_map` VALUES ('1107', '110', '52', '10', '10', '14', '14', '1', '0');
