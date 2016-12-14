/*
Navicat MySQL Data Transfer

Source Server         : 1
Source Server Version : 50626
Source Host           : 127.0.0.1:3306
Source Database       : battleship

Target Server Type    : MYSQL
Target Server Version : 50626
File Encoding         : 65001

Date: 2016-12-14 11:39:20
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
  `game_started` int(1) DEFAULT '0' COMMENT '0 - not started yet, 1 - game started',
  PRIMARY KEY (`map_id`),
  KEY `map_ibfk_1` (`server_id`),
  KEY `owner_id` (`owner_id`),
  CONSTRAINT `map_ibfk_1` FOREIGN KEY (`server_id`) REFERENCES `server` (`server_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `map_ibfk_2` FOREIGN KEY (`owner_id`) REFERENCES `player` (`player_id`)
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of map
-- ----------------------------
INSERT INTO `map` VALUES ('79', '2', 'dsaa', '48', '20', '0');
INSERT INTO `map` VALUES ('80', '2', 'dsad', '48', '40', '0');
INSERT INTO `map` VALUES ('81', '2', 'dasdas', '48', '20', '0');
INSERT INTO `map` VALUES ('82', '2', '111', '48', '40', '0');
INSERT INTO `map` VALUES ('83', '2', '333', '48', '20', '0');
INSERT INTO `map` VALUES ('84', '2', 'dsa', '48', '40', '0');

-- ----------------------------
-- Table structure for player
-- ----------------------------
DROP TABLE IF EXISTS `player`;
CREATE TABLE `player` (
  `player_id` int(11) NOT NULL AUTO_INCREMENT,
  `nickname` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`player_id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of player
-- ----------------------------
INSERT INTO `player` VALUES ('45', 'rrr');
INSERT INTO `player` VALUES ('46', 'sss');
INSERT INTO `player` VALUES ('47', 'dassad');
INSERT INTO `player` VALUES ('48', '123sa');
INSERT INTO `player` VALUES ('49', 'ff');

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
  `hit` int(11) DEFAULT NULL COMMENT 'If shot hit in someone = 1, otherwise 0',
  PRIMARY KEY (`shot_id`),
  KEY `player_hits_ibfk_1` (`map_id`),
  KEY `player_hits_ibfk_2` (`player_id`),
  CONSTRAINT `player_hits_ibfk_1` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `player_hits_ibfk_2` FOREIGN KEY (`player_id`) REFERENCES `player` (`player_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=251 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of player_hits
-- ----------------------------
INSERT INTO `player_hits` VALUES ('230', '83', '48', '17', '4', '2016-12-14 10:05:21', '0');
INSERT INTO `player_hits` VALUES ('231', '83', '48', '17', '5', '2016-12-14 10:05:28', '0');
INSERT INTO `player_hits` VALUES ('232', '83', '48', '16', '5', '2016-12-14 10:05:31', '0');
INSERT INTO `player_hits` VALUES ('233', '83', '48', '15', '6', '2016-12-14 10:05:35', '1');
INSERT INTO `player_hits` VALUES ('234', '83', '48', '15', '5', '2016-12-14 10:06:01', '0');
INSERT INTO `player_hits` VALUES ('235', '83', '48', '14', '5', '2016-12-14 10:06:02', '0');
INSERT INTO `player_hits` VALUES ('236', '83', '48', '14', '6', '2016-12-14 10:06:07', '0');
INSERT INTO `player_hits` VALUES ('237', '83', '48', '14', '7', '2016-12-14 10:06:09', '0');
INSERT INTO `player_hits` VALUES ('238', '83', '48', '15', '7', '2016-12-14 10:06:11', '0');
INSERT INTO `player_hits` VALUES ('239', '83', '48', '16', '7', '2016-12-14 10:06:12', '0');
INSERT INTO `player_hits` VALUES ('240', '83', '48', '16', '6', '2016-12-14 10:06:13', '1');
INSERT INTO `player_hits` VALUES ('241', '83', '48', '17', '6', '2016-12-14 10:06:15', '0');
INSERT INTO `player_hits` VALUES ('242', '83', '48', '2', '19', '2016-12-14 10:29:47', '0');
INSERT INTO `player_hits` VALUES ('243', '83', '48', '9', '13', '2016-12-14 10:59:51', '0');
INSERT INTO `player_hits` VALUES ('244', '83', '48', '16', '16', '2016-12-14 10:59:53', '0');
INSERT INTO `player_hits` VALUES ('245', '83', '48', '11', '14', '2016-12-14 10:59:53', '0');
INSERT INTO `player_hits` VALUES ('246', '83', '48', '10', '9', '2016-12-14 10:59:54', '1');
INSERT INTO `player_hits` VALUES ('247', '83', '48', '4', '12', '2016-12-14 11:15:27', '0');
INSERT INTO `player_hits` VALUES ('248', '83', '48', '7', '12', '2016-12-14 11:15:28', '0');
INSERT INTO `player_hits` VALUES ('249', '83', '48', '12', '13', '2016-12-14 11:15:29', '0');
INSERT INTO `player_hits` VALUES ('250', '83', '48', '19', '17', '2016-12-14 11:18:28', '0');

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
  PRIMARY KEY (`id`),
  KEY `player_to_map_ibfk_1` (`map_id`),
  KEY `player_to_map_ibfk_2` (`player_id`),
  CONSTRAINT `player_to_map_ibfk_1` FOREIGN KEY (`map_id`) REFERENCES `map` (`map_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `player_to_map_ibfk_2` FOREIGN KEY (`player_id`) REFERENCES `player` (`player_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of player_to_map
-- ----------------------------
INSERT INTO `player_to_map` VALUES ('1', '83', '45', '2016-12-14 06:17:48', '0');
INSERT INTO `player_to_map` VALUES ('2', '83', '48', '2016-12-14 00:21:26', '0');

-- ----------------------------
-- Table structure for server
-- ----------------------------
DROP TABLE IF EXISTS `server`;
CREATE TABLE `server` (
  `server_id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`server_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of server
-- ----------------------------
INSERT INTO `server` VALUES ('1', 'server1');
INSERT INTO `server` VALUES ('2', 'server2');
INSERT INTO `server` VALUES ('3', '123');

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
) ENGINE=InnoDB AUTO_INCREMENT=708 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of ship_to_map
-- ----------------------------
INSERT INTO `ship_to_map` VALUES ('688', '83', '48', '10', '10', '12', '15', '4', '0');
INSERT INTO `ship_to_map` VALUES ('689', '83', '48', '6', '8', '8', '8', '3', '0');
INSERT INTO `ship_to_map` VALUES ('690', '83', '48', '0', '0', '16', '18', '3', '0');
INSERT INTO `ship_to_map` VALUES ('691', '83', '48', '13', '13', '1', '2', '2', '0');
INSERT INTO `ship_to_map` VALUES ('692', '83', '48', '9', '10', '4', '4', '2', '0');
INSERT INTO `ship_to_map` VALUES ('693', '83', '48', '1', '1', '10', '11', '2', '0');
INSERT INTO `ship_to_map` VALUES ('694', '83', '48', '19', '19', '14', '14', '1', '0');
INSERT INTO `ship_to_map` VALUES ('695', '83', '48', '11', '11', '17', '17', '1', '0');
INSERT INTO `ship_to_map` VALUES ('696', '83', '48', '18', '18', '3', '3', '1', '0');
INSERT INTO `ship_to_map` VALUES ('697', '83', '48', '13', '13', '15', '15', '1', '0');
INSERT INTO `ship_to_map` VALUES ('698', '83', '45', '10', '10', '6', '9', '4', '0');
INSERT INTO `ship_to_map` VALUES ('699', '83', '45', '12', '14', '4', '4', '3', '0');
INSERT INTO `ship_to_map` VALUES ('700', '83', '45', '3', '5', '13', '13', '3', '0');
INSERT INTO `ship_to_map` VALUES ('701', '83', '45', '9', '10', '19', '19', '2', '0');
INSERT INTO `ship_to_map` VALUES ('702', '83', '45', '15', '15', '14', '15', '2', '0');
INSERT INTO `ship_to_map` VALUES ('703', '83', '45', '15', '16', '6', '6', '2', '0');
INSERT INTO `ship_to_map` VALUES ('704', '83', '45', '2', '2', '18', '18', '1', '0');
INSERT INTO `ship_to_map` VALUES ('705', '83', '45', '2', '2', '15', '15', '1', '0');
INSERT INTO `ship_to_map` VALUES ('706', '83', '45', '9', '9', '17', '17', '1', '0');
INSERT INTO `ship_to_map` VALUES ('707', '83', '45', '8', '8', '15', '15', '1', '0');
